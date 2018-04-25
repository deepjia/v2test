"""Views"""
import os
import re
import shutil
from multiprocessing import Process
from flask import request, render_template, session, redirect, \
    url_for, make_response, send_from_directory, flash, jsonify, current_app
import pyexcel as pe

from . import main
from .forms import LoginForm, RegForm, ProjectForm
from ..models import *


def log_user_in(userid, username):
    session['userid'] = userid
    session['username'] = username
    return redirect(url_for(".index"))

# 获取用例文件名


@main.app_template_global()
def getsuites(userid, projectid):
    path = testsuite_dir(userid, projectid)
    return (x.name for x in os.scandir(path) if x.is_file()
            and x.name.endswith(".xlsx") and '~$' not in x.name)


# 获取测试文件名
@main.app_template_global()
def getfiles(userid, projectid):
    path = testfile_dir(userid, projectid)
    return (x.name for x in os.scandir(path) if x.is_file())


# 首页（项目页面）
@main.route('/')
@main.route('/index')
def index():
    if 'username' in session:
        userid = session['userid']
        username = session['username']
        resp = make_response(render_template(
            'index.html', userid=userid, username=username, projects=get_projects(userid)))
        resp.set_cookie('username', username)
        return resp
    return redirect(url_for(".login"))


# 登录
@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        username = form.username.data
        if not form.validate_on_submit():
            for field in form.errors:
                for error in form.errors[field]:
                    flash(error, category='error')
        else:
            userid = valid_login(username, form.password.data)
            if userid is not None:
                return log_user_in(userid, username)
            else:
                flash('Invalid username/password', category='error')
        resp = make_response(redirect(url_for('.login')))
        resp.set_cookie('username', username)
        return resp
    elif 'userid' in session:
        return redirect(url_for(".index"))
    else:
        form.username.data = request.cookies.get('username')
        return render_template('login.html', form=form)


# 注册
@main.route('/reg', methods=['GET', 'POST'])
def reg():
    form = RegForm()
    if request.method == 'POST':
        username = form.username.data
        if not form.validate_on_submit():
            for field in form.errors:
                for error in form.errors[field]:
                    flash(error, category='error')
        # 验重
        elif get_userid(username):
            flash("User exists", category='error')
        # 创建用户
        else:
            create_user(username, form.password.data)
            userid = get_userid(username)
            # 登入
            return log_user_in(userid, username)
        return redirect(url_for('.reg'))
    else:
        return render_template('reg.html', form=RegForm())


# 登出
@main.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('userid', None)
    return redirect(url_for('.login'))


# 配置
@main.route('/edit', methods=['GET', 'POST'])
def edit():
    if 'username' not in session:
        return redirect(url_for(".login"))
    form = ProjectForm()
    userid = session['userid']
    projectid = request.args.get('projectid')
    config_path = os.path.join(
        current_app.root_path, 'user', userid, projectid, 'config.ini')
    if request.method == 'POST':
        # 项目校验 #
        errors = check_project_info(userid, form, projectid)
        if errors:
            for error in errors:
                flash(error, category='error')
            return redirect(url_for('.edit', projectid=projectid))
        # 修改项目
        else:
            # 项目改名
            rename_project(userid, projectid, form.projectname.data)
            # 修改模式
            set_projectmode(userid, projectid, form.mode.data)
            # 替换配置文件
            if form.configfile.data:
                save_files(project_dir(userid, projectid),
                           form.configfile.data)
            # 编辑配置文件
            else:
                with open(config_path, 'w') as f:
                    f.write(form.configcontent.data.replace('\r', ''))
                    f.close()
            # 增加测试套
            save_files(testsuite_dir(userid, projectid),
                       *form.testsuites.raw_data)
            # 增加测试文件
            save_files(testfile_dir(userid, projectid),
                       *form.testfiles.raw_data)
            flash('Project edited', category='info')
            return redirect(url_for(".index"))
    # GET 请求
    else:
        with open(config_path, 'r') as f:
            form.configcontent.data = f.read()
            f.close()
        form.mode.data = str(get_projectmode(userid, projectid))
        form.projectname.data = get_projectname(userid, projectid)
        return render_template('edit.html', userid=userid, projectid=projectid, form=form)


# 添加项目
@main.route('/add', methods=['GET', 'POST'])
def add():
    if 'username' not in session:
        return redirect(url_for(".login"))
    form = ProjectForm()
    userid = session['userid']
    if request.method == 'POST':
        # 项目校验 #
        errors = check_project_info(userid, form)
        if errors:
            for error in errors:
                flash(error, category='error')
            return redirect(url_for(".add"))
        else:
            projectid = create_project(
                form.projectname.data, userid, form.mode.data)
            config_path = os.path.join(
                project_dir(userid, projectid), 'config.ini')
            # 保存配置文件
            if form.configfile.data:
                save_files(project_dir(userid, projectid),
                           form.configfile.data)
            # 无配置文件时，加载默认模版，并按需修改
            else:
                shutil.copy(current_app.config['TEMPLATE_CONFIG'], config_path)
                configcontent = form.configcontent.data
                if configcontent:
                    with open(config_path, 'w') as f:
                        f.write(configcontent.replace('\r', ''))
                        f.close()
            # 保存测试套
            save_files(testsuite_dir(userid, projectid),
                       *form.testsuites.raw_data)
            # 保存测试文件
            save_files(testfile_dir(userid, projectid),
                       *form.testfiles.raw_data)
            flash('Project added', category='info')
            return redirect(url_for(".index"))
    else:
        form.mode.data = '0'
        return render_template('add.html', form=form)


@main.route('/dl_testsuite')
def dl_testsuite():
    if 'username' not in session:
        return redirect(url_for(".login"))
    userid = session['userid']
    projectid = request.args.get('projectid')
    filename = request.args.get('filename')
    directory = os.path.join(
        current_app.root_path, 'user', userid, projectid, current_app.config['TESTSUITE_DIR'])
    return send_from_directory(directory, filename, as_attachment=True)


@main.route('/dl_template')
def dl_template():
    directory = current_app.config['DOWNOAD']
    return send_from_directory(directory, current_app.config['TEMPLATE_NAME'], as_attachment=True)


# 测试文件和脚本
@main.route('/dl_testfile')
def dl_testfile():
    if 'username' not in session:
        return redirect(url_for(".login"))
    userid = session['userid']
    projectid = request.args.get('projectid')
    filename = request.args.get('filename')
    directory = os.path.join(
        current_app.root_path, 'user', userid, projectid, current_app.config['TESTFILE_DIR'])
    return send_from_directory(directory, filename, as_attachment=True)


# 下载测试报告
@main.route('/dl_testreport')
def dl_testreport():
    if 'username' not in session:
        return redirect(url_for(".login"))
    userid = session['userid']
    projectid = request.args.get('projectid')
    filename = request.args.get('filename')
    directory = os.path.join(
        current_app.root_path, 'user', userid, projectid, current_app.config['TESTREPORT_DIR'])
    return send_from_directory(directory, filename, as_attachment=True)


# 报告列表
@main.route('/reports')
def reports():
    if 'username' not in session:
        return redirect(url_for(".login"))
    userid = session['userid']
    projectid = request.args.get('projectid')
    testreports = getreports(userid, projectid)
    return render_template('reports.html', reports=testreports, projectid=projectid,
                           projectname=get_projectname(userid, projectid))


# 报告
@main.route('/report')
def report():
    if 'username' not in session:
        return redirect(url_for(".login"))
    userid = session['userid']
    projectid = request.args.get('projectid')
    reportdir = testreport_dir(userid, projectid)
    testreport = request.args.get('report')
    reportpath = os.path.join(reportdir, testreport)
    with open(reportpath, 'r') as f:
        reportcontent = f.read()
        f.close()
    reportcontent = reportcontent.split('<body>', 1)[1].rsplit(
        '</body>', 1)[0].replace('V2Test Report', testreport)
    return render_template('report.html', report=testreport, reportcontent=reportcontent, projectid=projectid)


@main.route('/testsuite')
def testsuite():
    if 'username' not in session:
        return redirect(url_for(".login"))
    userid = session['userid']
    projectid = request.args.get('projectid')
    suitedir = testsuite_dir(userid, projectid)
    testsuite = request.args.get('testsuite')
    suitepath = os.path.join(suitedir, testsuite)
    book = pe.get_book(file_name=suitepath)
    testsuitecontent = book.html.replace("<table>", "<table class='table table-bordered table-hover table-condensed'>")
    testsuitecontent = re.sub(r'<tbody>\n<tr>', r'<tbody>\n<tr class="warning">', testsuitecontent)
    testsuitecontent = re.sub(r'<tr><td>([^<>]*[^ <>]+[^<>]*)</td>',r'<tr class="success"><td>\1</td>', testsuitecontent)
    return render_template('testsuite.html', testsuite=testsuite, testsuitecontent=testsuitecontent, projectid=projectid)


# 删除项目
@main.route('/delete_project', methods=['POST'])
def delete_project():
    if 'username' not in session:
        return redirect(url_for(".login"))
    projectid = request.form['projectid']
    userid = session['userid']
    if project_owner(projectid) == userid:
        rm_project(projectid, userid)
        flash('Project deleted', category='info')
        return jsonify({'status': 'success'})
    else:
        flash('Project not exists or permission deny', category='error')
        return jsonify({'status': 'fail'})


@main.route('/delete_testsuite', methods=['POST'])
def delete_testsuite():
    if 'username' not in session:
        return redirect(url_for(".login"))
    projectid = request.form['projectid']
    file_to_del = request.form['filename']
    userid = session['userid']
    if project_owner(projectid) == userid:
        os.remove(os.path.join(testsuite_dir(userid, projectid), file_to_del))
        flash('TestSuite deleted', category='info')
        return jsonify({'status': 'success'})
    else:
        flash('File not exists or permission deny', category='error')
        return jsonify({'status': 'fail'})


@main.route('/delete_testfile', methods=['POST'])
def delete_testfile():
    if 'username' not in session:
        return redirect(url_for(".login"))
    projectid = request.form['projectid']
    file_to_del = request.form['filename']
    userid = session['userid']
    if project_owner(projectid) == userid:
        os.remove(os.path.join(testfile_dir(userid, projectid), file_to_del))
        flash('TestFile deleted', category='info')
        return jsonify({'status': 'success'})
    else:
        flash('File not exists or permission deny', category='error')
        return jsonify({'status': 'fail'})


@main.route('/delete_testreport', methods=['POST'])
def delete_testreport():
    if 'username' not in session:
        return redirect(url_for(".login"))
    projectid = request.form['projectid']
    file_to_del = request.form['filename']
    userid = session['userid']
    if project_owner(projectid) == userid:
        os.remove(os.path.join(testreport_dir(userid, projectid), file_to_del))
        flash('TestReport deleted', category='info')
        return jsonify({'status': 'success'})
    else:
        flash('File not exists or permission deny', category='error')
        return jsonify({'status': 'fail'})


@main.route('/run', methods=['POST'])
def run():
    if 'username' not in session:
        return redirect(url_for(".login"))
    userid = session['userid']
    projectid = request.form['projectid']
    mode = get_projectmode(userid, projectid)
    shutil.rmtree(runsuite_dir(userid, projectid), ignore_errors=True)
    shutil.rmtree(runfile_dir(userid, projectid), ignore_errors=True)
    if mode == 0:
        shutil.copytree(testsuite_dir(userid, projectid),
                        runsuite_dir(userid, projectid))
        shutil.copytree(testfile_dir(userid, projectid),
                        runfile_dir(userid, projectid))
        p = Process(target=runlocal, args=(userid, projectid))
        p.start()
    elif mode == 1:
        shutil.copytree(testsuite_dir(userid, projectid), os.path.join(
            runsuite_dir(userid, projectid), 'DEFAULT'))
        shutil.copytree(testfile_dir(userid, projectid), os.path.join(
            runfile_dir(userid, projectid), 'DEFAULT'))
        p = Process(target=runremote, args=(userid, projectid))
        p.start()
    set_projectstatus(userid, projectid, 'Running')
    flash('Project start running', category='info')
    return jsonify({'status': 'success'})

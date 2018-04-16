#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import shutil
import sqlite3
import sys
import subprocess
from multiprocessing import Process
from flask import Flask, request, render_template, g, session, redirect, \
    url_for, make_response, escape, send_from_directory
from werkzeug.utils import secure_filename
from model import *


# 获取用例文件名
@app.template_global()
def getsuites(userid, projectid):
    path = testsuite_dir(userid, projectid)
    return (x.name for x in os.scandir(path) if x.is_file()
            and x.name.endswith(".xlsx") and '~$' not in x.name)


# 获取测试文件名
@app.template_global()
def getfiles(userid, projectid):
    path = testfile_dir(userid, projectid)
    return (x.name for x in os.scandir(path) if x.is_file())


# 首页（项目页面）
@app.route('/')
@app.route('/index')
def index():
    if 'username' in session:
        userid = session['userid']
        username = session['username']
        info = request.args.get('info')
        error = request.args.get('error')
        resp = make_response(render_template(
            'index.html', userid=userid, username=username, projects=get_projects(userid), info=info, error=error))
        resp.set_cookie('username', username)
        return resp
    return redirect(url_for("login"))


# 登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        userid = valid_login(username, request.form['password'])
        if userid is not None:
            return log_user_in(userid, username)
        else:
            error = 'Invalid username/password'
    elif 'userid' in session:
        return redirect(url_for("index"))
    return render_template('login.html', error=error, lastusername=request.cookies.get('username'))


# 注册
@app.route('/reg', methods=['GET', 'POST'])
def reg():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password2 = request.form['password2']
        if not username:
            error = "Username required"
        elif not password:
            error = "Password required"
        # 验重
        elif get_userid(username):
            error = "User exists"
        elif password != password2:
            error = "Passwords did not match"
        else:
            # 创建用户
            create_user(username, request.form['password'])
            userid = get_userid(username)
            # 登入
            return log_user_in(userid, username)
    return render_template('reg.html', error=error)


# 登出
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('userid', None)
    return redirect(url_for('login'))


# 配置
@app.route('/config', methods=['GET', 'POST'])
def config():
    userid = session['userid']
    projectid = request.args.get('projectid')
    info = request.args.get('info')
    error = request.args.get('error')
    config_path = os.path.join(
        app.root_path, 'user', userid, projectid, 'config.ini')
    if request.method == 'POST':
        configcontent = request.form['configcontent']
        configfiles = request.files.getlist('configfile')
        testsuites = request.files.getlist('testsuites')
        testfiles = request.files.getlist('testfiles')
        projectname = request.form['projectname']
        error = check_project_info(
            userid, projectname, configfiles, testsuites, testfiles, projectid)
        if error is None:
            rename_project(projectid, userid, projectname)
            if configfiles:
                save_files(project_dir(userid, projectid), configfiles)
            else:
                with open(config_path, 'w') as f:
                    f.write(configcontent.replace('\r', ''))
                    f.close()
            save_files(testsuite_dir(userid, projectid), testsuites,)
            save_files(testfile_dir(userid, projectid), testfiles)
            return redirect(url_for("index", info="Project edited"))
    projectname = get_projectname(userid, projectid)
    with open(config_path, 'r') as f:
        configcontent = f.read()
        f.close()
    return render_template('config.html', userid=userid, projectid=projectid, projectname=projectname,
                           configcontent=configcontent, info=info, error=error)


@app.route('/dl_testsuite')
def dl_testsuite():
    userid = session['userid']
    projectid = request.args.get('projectid')
    filename = request.args.get('filename')
    directory = os.path.join(
        app.root_path, 'user', userid, projectid, TESTSUITE_DIR)
    return send_from_directory(directory, filename, as_attachment=True)


@app.route('/dl_template')
def dl_template():
    directory = app.config['DOWNOAD']
    return send_from_directory(directory, TEMPLATE_NAME, as_attachment=True)


# 测试文件和脚本
@app.route('/dl_testfile')
def dl_testfile():
    userid = session['userid']
    projectid = request.args.get('projectid')
    filename = request.args.get('filename')
    directory = os.path.join(
        app.root_path, 'user', userid, projectid, TESTFILE_DIR)
    return send_from_directory(directory, filename, as_attachment=True)


# 下载测试报告
@app.route('/dl_testreport')
def dl_testreport():
    userid = session['userid']
    projectid = request.args.get('projectid')
    filename = request.args.get('filename')
    directory = os.path.join(
        app.root_path, 'user', userid, projectid, TESTREPORT_DIR)
    return send_from_directory(directory, filename, as_attachment=True)
    

# 报告列表
@app.route('/reports')
def reports():
    info = request.args.get('info')
    error = request.args.get('error')
    userid = session['userid']
    projectid = request.args.get('projectid')
    testreports = getreports(userid, projectid)
    return render_template('reports.html', reports=testreports, projectid=projectid,
                           projectname=get_projectname(userid, projectid), error=error, info=info)


# 报告
@app.route('/report')
def report():
    userid = session['userid']
    projectid = request.args.get('projectid')
    reportdir = testreport_dir(userid, projectid)
    testreport = request.args.get('report')
    reportpath = os.path.join(reportdir, testreport)
    with open(reportpath, 'r') as f:
        reportcontent = f.read()
        f.close()
    reportcontent = reportcontent.split('<body>', 1)[1].rsplit('</body>', 1)[0].replace('V2Test Report', testreport)
    return render_template('report.html', report=testreport, reportcontent=reportcontent, projectid=projectid)


# 添加项目
@app.route('/add', methods=['GET', 'POST'])
def add():
    # error = request.args.get('error')
    error = None
    userid = session['userid']
    if request.method == 'POST':
        configcontent = request.form['configcontent']
        configfiles = request.files.getlist('configfile')
        testsuites = request.files.getlist('testsuites')
        testfiles = request.files.getlist('testfiles')
        project = request.form['project']
        error = check_project_info(
            userid, project, configfiles, testsuites, testfiles)
        if error is None:
            projectid = create_project(project, userid)
            config_path = os.path.join(
                project_dir(userid, projectid), 'config.ini')
            if configfiles:
                save_files(project_dir(userid, projectid), configfiles)
            else:
                shutil.copy(app.config['TEMPLATE_CONFIG'], config_path)
                if configcontent:
                    with open(config_path, 'w') as f:
                        f.write(configcontent.replace('\r', ''))
                        f.close()
            save_files(testsuite_dir(userid, projectid), testsuites)
            save_files(testfile_dir(userid, projectid), testfiles)
            return redirect(url_for("index", info='Project added'))
    return render_template('add.html', error=error)


# 删除项目
@app.route('/delete_project', methods=['POST'])
def delete_project():
    res = {}
    projectid = request.form['projectid']
    userid = session['userid']
    if project_owner(projectid) == userid:
        rm_project(projectid, userid)
        res['info'] = 'Project deleted'
    else:
        res['error'] = 'File not exists or permission deny'
    return json.dumps(res)


@app.route('/delete_testsuite', methods=['POST'])
def delete_testsuite():
    res = {}
    projectid = request.form['projectid']
    file_to_del = request.form['filename']
    userid = session['userid']
    if project_owner(projectid) == userid:
        os.remove(os.path.join(testsuite_dir(userid, projectid), file_to_del))
        res['info'] = 'TestSuite deleted'
    else:
        res['error'] = 'File not exists or permission deny'
    return json.dumps(res)


@app.route('/delete_testfile', methods=['POST'])
def delete_testfile():
    res = {}
    projectid = request.form['projectid']
    file_to_del = request.form['filename']
    userid = session['userid']
    if project_owner(projectid) == userid:
        os.remove(os.path.join(testfile_dir(userid, projectid), file_to_del))
        res['info'] = 'TestFile deleted'
    else:
        res['error'] = 'File not exists or permission deny'
    return json.dumps(res)


@app.route('/delete_testreport', methods=['POST'])
def delete_testreport():
    res = {}
    projectid = request.form['projectid']
    file_to_del = request.form['filename']
    userid = session['userid']
    if project_owner(projectid) == userid:
        os.remove(os.path.join(testreport_dir(userid, projectid), file_to_del))
        res['info'] = 'TestReport deleted'
    else:
        res['error'] = 'File not exists or permission deny'
    return json.dumps(res)


@app.route('/run', methods=['POST'])
def run():
    res = {}
    userid = session['userid']
    projectid = request.form['projectid']
    mode = get_projectmode(userid,projectid)
    shutil.rmtree(runsuite_dir(userid, projectid), ignore_errors=True)
    shutil.rmtree(runfile_dir(userid, projectid), ignore_errors=True)
    if mode == 0:
        shutil.copytree(testsuite_dir(userid, projectid), runsuite_dir(userid, projectid))
        shutil.copytree(testfile_dir(userid, projectid), runfile_dir(userid, projectid))
        p = Process(target=runlocal,args=(userid, projectid))
        p.start()
    elif mode == 1:
        shutil.copytree(testsuite_dir(userid, projectid), os.path.join(runsuite_dir(userid, projectid),'DEFAULT'))
        shutil.copytree(testfile_dir(userid, projectid), os.path.join(runfile_dir(userid, projectid),'DEFAULT'))
        p = Process(target=runremote,args=(userid, projectid))
        p.start()
    res['info'] = 'Project start running'
    set_projectstatus(userid,projectid,'Running')
    return json.dumps(res)


def runlocal(userid, projectid):
    r = subprocess.run([sys.executable, '../run.py', userid, projectid], stdout=subprocess.PIPE)
    if r.returncode:
        # error
        set_projectstatus(userid, projectid, 'Failing')
    else:
        set_projectstatus(userid, projectid,'Passing')


def runremote(userid, projectid):
    r = subprocess.run([sys.executable, '../run.py', userid, projectid], stdout=subprocess.PIPE)
    if r.returncode:
        # error
        set_projectstatus(userid, projectid, 'Failing')
    else:
        set_projectstatus(userid, projectid,'Need confirmation')


if __name__ == '__main__':
    app.run()

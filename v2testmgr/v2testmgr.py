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
    url_for, make_response, escape, send_from_directory, flash, jsonify
from werkzeug.utils import secure_filename
from model import *
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextField, PasswordField, RadioField, FileField, TextAreaField, RadioField
from wtforms.validators import InputRequired, EqualTo, Length
import pyexcel as pe


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
                           InputRequired(message='Username required')])
    password = PasswordField('Password', validators=[
                             InputRequired(message='Password required')])
    submit = SubmitField('Login')
    reg = SubmitField('Register')


class RegForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(
        message='Username required'), Length(min=3, max=25, message='Username should be 3-25 chars')])
    password = PasswordField('Password', validators=[InputRequired(
        message='Password required'), Length(min=3, max=30, message='Password should be 3-30 chars')])
    confirm = PasswordField('Confirm Password', validators=[InputRequired(
        message='Please confirm password'), EqualTo('password', message='Passwords mismatch')])
    submit = SubmitField('Register')
    cancel = SubmitField('Cancel')


class ProjectForm(FlaskForm):
    projectname = StringField('Project Name', validators=[InputRequired(
        message='Project name required'), Length(min=4, max=25, message='Project name should be 4-25 chars')])
    testsuites = FileField('TestSuites')
    testfiles = FileField('TestFiles')
    configfile = FileField('Config File')
    configcontent = TextAreaField('Edit Config')
    mode = RadioField('Run Mode',choices=[('0','Local'),('1','Remote')])
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel')


# 首页（项目页面）
@app.route('/')
@app.route('/index')
def index():
    if 'username' in session:
        userid = session['userid']
        username = session['username']
        resp = make_response(render_template(
            'index.html', userid=userid, username=username, projects=get_projects(userid)))
        resp.set_cookie('username', username)
        return resp
    return redirect(url_for("login"))


# 登录
@app.route('/login', methods=['GET', 'POST'])
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
        resp = make_response(redirect(url_for('login')))
        resp.set_cookie('username', username)
        return resp
    elif 'userid' in session:
        return redirect(url_for("index"))
    else:
        form.username.data = request.cookies.get('username')
        return render_template('login.html', form=form)


# 注册
@app.route('/reg', methods=['GET', 'POST'])
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
        return redirect(url_for('reg'))
    else:
        return render_template('reg.html', form=RegForm())


# 登出
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('userid', None)
    return redirect(url_for('login'))


# 配置
@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if 'username' not in session:
         return redirect(url_for("login"))
    form = ProjectForm()
    userid = session['userid']
    projectid = request.args.get('projectid')
    config_path = os.path.join(
        app.root_path, 'user', userid, projectid, 'config.ini')
    if request.method == 'POST':
        # 项目校验 #
        if not check_project_info(userid, form, projectid):
            return redirect(url_for('edit', projectid=projectid))
        # 修改项目
        else:
            # 项目改名
            rename_project(userid, projectid, form.projectname.data)
            # 修改模式
            set_projectmode(userid, projectid, form.mode.data)
            # 替换配置文件
            if form.configfile.data:
                save_files(project_dir(userid, projectid), form.configfile.data)
            # 编辑配置文件
            else:
                with open(config_path, 'w') as f:
                    f.write(form.configcontent.data.replace('\r', ''))
                    f.close()
            # 增加测试套
            save_files(testsuite_dir(userid, projectid), *form.testsuites.raw_data)
            # 增加测试文件
            save_files(testfile_dir(userid, projectid), *form.testfiles.raw_data)
            flash('Project edited', category='info')
            return redirect(url_for("index"))
    # GET 请求
    else:
        with open(config_path, 'r') as f:
            form.configcontent.data = f.read()
            f.close()
        form.mode.data = str(get_projectmode(userid, projectid))
        form.projectname.data = get_projectname(userid, projectid)
        return render_template('edit.html', userid=userid, projectid=projectid, form=form)


# 添加项目
@app.route('/add', methods=['GET', 'POST'])
def add():
    if 'username' not in session:
         return redirect(url_for("login"))
    form = ProjectForm()
    userid = session['userid']
    if request.method == 'POST':
        # 项目校验 #
        if check_project_info(userid, form):
            projectid = create_project(form.projectname.data, userid, form.mode.data)
            config_path = os.path.join(
                project_dir(userid, projectid), 'config.ini')
            # 保存配置文件
            if form.configfile.data:
                save_files(project_dir(userid, projectid), form.configfile.data)
            # 无配置文件时，加载默认模版，并按需修改
            else:
                shutil.copy(app.config['TEMPLATE_CONFIG'], config_path)
                configcontent = form.configcontent.data
                if configcontent:
                    with open(config_path, 'w') as f:
                        f.write(configcontent.replace('\r', ''))
                        f.close()
            # 保存测试套
            save_files(testsuite_dir(userid, projectid), *form.testsuites.raw_data)
            # 保存测试文件
            save_files(testfile_dir(userid, projectid), *form.testfiles.raw_data)
            flash('Project added', category='info')
            return redirect(url_for("index"))
        else:
            return redirect(url_for("add"))
    else:
        form.mode.data = '0'
        return render_template('add.html', form=form)


@app.route('/dl_testsuite')
def dl_testsuite():
    if 'username' not in session:
         return redirect(url_for("login"))
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
    if 'username' not in session:
         return redirect(url_for("login"))
    userid = session['userid']
    projectid = request.args.get('projectid')
    filename = request.args.get('filename')
    directory = os.path.join(
        app.root_path, 'user', userid, projectid, TESTFILE_DIR)
    return send_from_directory(directory, filename, as_attachment=True)


# 下载测试报告
@app.route('/dl_testreport')
def dl_testreport():
    if 'username' not in session:
         return redirect(url_for("login"))
    userid = session['userid']
    projectid = request.args.get('projectid')
    filename = request.args.get('filename')
    directory = os.path.join(
        app.root_path, 'user', userid, projectid, TESTREPORT_DIR)
    return send_from_directory(directory, filename, as_attachment=True)


# 报告列表
@app.route('/reports')
def reports():
    if 'username' not in session:
         return redirect(url_for("login"))
    userid = session['userid']
    projectid = request.args.get('projectid')
    testreports = getreports(userid, projectid)
    return render_template('reports.html', reports=testreports, projectid=projectid,
                           projectname=get_projectname(userid, projectid))


# 报告
@app.route('/report')
def report():
    if 'username' not in session:
         return redirect(url_for("login"))
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


@app.route('/testsuite')
def testsuite():
    if 'username' not in session:
         return redirect(url_for("login"))
    userid = session['userid']
    projectid = request.args.get('projectid')
    suitedir = testsuite_dir(userid, projectid)
    testsuite = request.args.get('testsuite')
    suitepath = os.path.join(suitedir, testsuite)
    sheet = pe.get_sheet(file_name=suitepath)
    testsuitecontent = sheet.html.replace("<table>", "<table class='table table-striped table-bordered table-hover table-condensed'>")
    return render_template('testsuite.html', testsuite=testsuite, testsuitecontent=testsuitecontent, projectid=projectid)


# 删除项目
@app.route('/delete_project', methods=['POST'])
def delete_project():
    if 'username' not in session:
         return redirect(url_for("login"))
    projectid = request.form['projectid']
    userid = session['userid']
    if project_owner(projectid) == userid:
        rm_project(projectid, userid)
        flash('Project deleted', category='info')
        return jsonify({'status': 'success'})
    else:
        flash('Project not exists or permission deny', category='error')
        return jsonify({'status': 'fail'})


@app.route('/delete_testsuite', methods=['POST'])
def delete_testsuite():
    if 'username' not in session:
         return redirect(url_for("login"))
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


@app.route('/delete_testfile', methods=['POST'])
def delete_testfile():
    if 'username' not in session:
         return redirect(url_for("login"))
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


@app.route('/delete_testreport', methods=['POST'])
def delete_testreport():
    if 'username' not in session:
         return redirect(url_for("login"))
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


@app.route('/run', methods=['POST'])
def run():
    if 'username' not in session:
         return redirect(url_for("login"))
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


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run()

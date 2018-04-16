#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import shutil
import sqlite3
import sys
import subprocess
from flask import Flask, request, render_template, g, session, redirect, \
    url_for, make_response, escape, send_from_directory
from werkzeug.utils import secure_filename


TESTSUITE_DIR = 'TestSuites'
TESTFILE_DIR = 'TestFiles'
TESTREPORT_DIR = 'TestReports'
TEMPLATE_DIR = 'templates'
CONFIG_NAME = 'config.ini'
TEMPLATE_NAME = 'template.zip'


app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'v2testmgr.db'),
    SECRET_KEY='development_temp_key',
    USERNAME='admin',
    PASSWORD='default'
))

app.config.from_envvar('FLASKR_SETTINGS', silent=True)
app.config['TEMPLATE_CONFIG'] = os.path.join(
    app.root_path, 'templates', 'config.ini')
app.config['DOWNOAD'] = os.path.join(app.root_path, 'download')


def testsuite_dir(userid, projectid):
    return os.path.join(app.root_path, 'user', userid, projectid, 'TestSuites')


def testfile_dir(userid, projectid):
    return os.path.join(app.root_path, 'user', userid, projectid, 'TestFiles')


def testreport_dir(userid, projectid):
    return os.path.join(app.root_path, 'user', userid, projectid, 'TestReports')

    
def runsuite_dir(userid, projectid):
    return os.path.join(app.root_path, 'user', userid, projectid, 'RunSuites')


def runfile_dir(userid, projectid):
    return os.path.join(app.root_path, 'user', userid, projectid, 'RunFiles')


def runreport_dir(userid, projectid):
    return os.path.join(app.root_path, 'user', userid, projectid, 'RunReports')


def project_dir(userid, projectid):
    return os.path.join(app.root_path, 'user', userid, projectid)


def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def get_userid(username):
    db = get_db()
    cur = db.execute(
        'SELECT uid FROM tb_user WHERE username="{0}"'.format(username))
    res = cur.fetchone()
    if res:
        return res[0]


def create_user(username, password):
    db = get_db()
    # 建用户
    cur = db.cursor()
    cur.execute('INSERT INTO tb_user (username, password) VALUES(?, ?)', [
                username, password])
    db.commit()
    return cur.lastrowid


# 保存文件
def save_files(directory, files):
    for file in files:
        filename = secure_filename(file.filename)
        # src = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        dst = os.path.join(directory, filename)
        file.save(dst)
        # shutil.move(src, dst)


# 用户的项目列表
def get_projects(userid):
    db = get_db()
    cur = db.execute(
        'SELECT pid, project, status, mode FROM tb_project WHERE uid=?', [userid])
    return cur.fetchall()


# 登入用户
def log_user_in(userid, username):
    session['userid'] = userid
    session['username'] = username
    return redirect(url_for("index"))


# 登录校验
def valid_login(username, password):
    db = get_db()
    cur = db.execute('SELECT uid FROM tb_user WHERE username=? and password=?', [
                     username, password])
    res = cur.fetchone()
    if res:
        return str(res[0])


# 检查项目归属
def project_owner(projectid):
    db = get_db()
    cur = db.execute('SELECT uid FROM tb_project WHERE pid=?', [projectid])
    res = cur.fetchone()
    if res:
        return str(res[0])


# 获取项目id
def get_projectid(userid, project):
    db = get_db()
    cur = db.execute(
        'SELECT pid FROM tb_project WHERE uid=? AND project=?', [userid, project])
    res = cur.fetchone()
    if res:
        return str(res[0])


# 获取项目名
def get_projectname(userid, projectid):
    db = get_db()
    cur = db.execute(
        'SELECT project FROM tb_project WHERE uid=? AND pid=?', [userid, projectid])
    res = cur.fetchone()
    if res:
        return str(res[0])


# 检查项目信息
def check_project_info(userid, project, configfiles, testsuites, testfiles, projectid=None):
    error = None
    if not project:
        error = "Project name is requried."
    # 检查项目是否存在
    else:
        existid = get_projectid(userid, project)
        if existid and existid != projectid:
            error = "Project exists."
    # 检查文件
    if configfiles:
        if configfiles[0].filename.endswith('.ini'):
            configfiles[0].filename = CONFIG_NAME
        else:
            error = "Invalid Config file, only ini accepted"
    if testsuites:
        for testsuite in testsuites:
            if not testsuite.filename.endswith('.xlsx'):
                error = 'Invalid TestSuites, only xlsx accepted'
                break
    if testfiles:
        for testfile in testfiles:
            if testfile.filename == '':
                error = 'Invalid TestFiles'
                break
    return error


# 创建项目
def create_project(project, userid, mode):
    db = get_db()
    # 建用户
    cur = db.cursor()
    cur.execute('INSERT INTO tb_project (project, uid, mode) VALUES(?, ?, ?)', [
        project, userid, mode])
    projectid = str(cur.lastrowid)
    db.commit()
    os.makedirs(testsuite_dir(userid, projectid))
    os.makedirs(testfile_dir(userid, projectid))
    os.makedirs(testreport_dir(userid, projectid))
    return projectid


# 项目改名
def rename_project(userid, projectid, projectname):
    db = get_db()
    db.execute('UPDATE tb_project SET project=? WHERE uid=? AND pid=?', [projectname, userid, projectid])
    db.commit()


def rm_project(projectid, userid):
    db = get_db()
    # 建用户
    cur = db.cursor()
    cur.execute('delete from tb_project WHERE pid=? AND uid=?', [
        projectid, userid])
    db.commit()
    shutil.rmtree(project_dir(userid, projectid))


def getreports(userid, projectid):
    res = []
    path = testreport_dir(userid, projectid)
    for reportfile in os.scandir(path):
        if reportfile.is_file() and reportfile.name.endswith(".html"):
            with open(reportfile.path, 'r') as f:
                reportcontent = f.read()
                f.close()
            res.append((reportfile.name, reportcontent.split('<strong>Start Time: </strong>', 1)[1].split(
                '</p>', 1)[0], reportcontent.split('<strong>Status: </strong>', 1)[1].split('</p>', 1)[0]))
    return sorted(res, reverse=True)


def get_projectmode(userid, projectid):
    db = get_db()
    cur = db.execute(
        'SELECT mode FROM tb_project WHERE uid=? AND pid=?', [userid, projectid])
    res = cur.fetchone()
    if res:
        # integer 
        return res[0]

def set_projectstatus(userid, projectid, status):
    db = get_db()
    db.execute('UPDATE tb_project SET status=? WHERE uid=? AND pid=?', [status, userid, projectid])
    db.commit()
    

def set_projectmode(userid, projectid, mode):
    db = get_db()
    db.execute('UPDATE tb_project SET mode=? WHERE uid=? AND pid=?', [mode, userid, projectid])
    db.commit()


def runlocal(userid, projectid):
    r = subprocess.run([sys.executable, os.path.join(app.root_path,'..','run.py'), userid, projectid], stdout=subprocess.PIPE)
    if r.returncode:
        # error
        set_projectstatus(userid, projectid, 'Failing')
    else:
        set_projectstatus(userid, projectid,'Passing')


def runremote(userid, projectid):
    r = subprocess.run([sys.executable, os.path.join(app.root_path,'..','sender.py'), userid, projectid], stdout=subprocess.PIPE)
    if r.returncode:
        # error
        set_projectstatus(userid, projectid, 'Failing')
    else:
        set_projectstatus(userid, projectid,'Need confirmation')
        

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

    
app.secret_key = 'ASDGWErs923#$%^^^^=='

if __name__ == '__main__':
    app.run()

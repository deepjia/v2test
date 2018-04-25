#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import shutil
import sys
import subprocess
from flask import current_app
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash,check_password_hash
from . import sqlitedb




def testsuite_dir(userid, projectid):
    return os.path.join(current_app.root_path, 'user', userid, projectid, 'TestSuites')


def testfile_dir(userid, projectid):
    return os.path.join(current_app.root_path, 'user', userid, projectid, 'TestFiles')


def testreport_dir(userid, projectid):
    return os.path.join(current_app.root_path, 'user', userid, projectid, 'TestReports')


def runsuite_dir(userid, projectid):
    return os.path.join(current_app.root_path, 'user', userid, projectid, 'RunSuites')


def runfile_dir(userid, projectid):
    return os.path.join(current_app.root_path, 'user', userid, projectid, 'RunFiles')


def runreport_dir(userid, projectid):
    return os.path.join(current_app.root_path, 'user', userid, projectid, 'RunReports')


def project_dir(userid, projectid):
    return os.path.join(current_app.root_path, 'user', userid, projectid)


def get_userid(username):
    db = sqlitedb.connection
    cur = db.execute(
        'SELECT uid FROM tb_user WHERE username="{0}"'.format(username))
    res = cur.fetchone()
    if res:
        return str(res[0])


def create_user(username, password):
    db = sqlitedb.connection
    # 建用户
    password_hash = generate_password_hash(password)
    cur = db.cursor()
    cur.execute('INSERT INTO tb_user (username, password) VALUES(?, ?)', [
                username, password_hash])
    db.commit()
    return cur.lastrowid


# 保存文件
def save_files(directory, *files):
    for file in filter(None, files):
        filename = secure_filename(file.filename)
        # src = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        dst = os.path.join(directory, filename)
        file.save(dst)
        # shutil.move(src, dst)


# 用户的项目列表
def get_projects(userid):
    db = sqlitedb.connection
    cur = db.execute(
        'SELECT pid, project, status, mode FROM tb_project WHERE uid=?', [userid])
    return cur.fetchall()


# 登录校验
def valid_login(username, password):
    db = sqlitedb.connection
    cur = db.execute('SELECT uid,password FROM tb_user WHERE username=?', [
                     username])
    res = cur.fetchone()
    if res and check_password_hash(res[1],password):
        return str(res[0])


# 检查项目归属
def project_owner(projectid):
    db = sqlitedb.connection
    cur = db.execute('SELECT uid FROM tb_project WHERE pid=?', [projectid])
    res = cur.fetchone()
    if res:
        return str(res[0])


# 获取项目id
def get_projectid(userid, project):
    db = sqlitedb.connection
    cur = db.execute(
        'SELECT pid FROM tb_project WHERE uid=? AND project=?', [userid, project])
    res = cur.fetchone()
    if res:
        return str(res[0])


# 获取项目名
def get_projectname(userid, projectid):
    db = sqlitedb.connection
    cur = db.execute(
        'SELECT project FROM tb_project WHERE uid=? AND pid=?', [userid, projectid])
    res = cur.fetchone()
    if res:
        return str(res[0])


# 检查项目信息
def check_project_info(userid, form, projectid=None):
    errors = []
    # 项目名校验
    if not form.validate_on_submit():
        for field in form.errors:
            for error in form.errors[field]:
                errors.append(error)
    else:
        existid = get_projectid(userid, form.projectname.data)
        if existid and existid != projectid:
            errors.append("Project exists.")
    # 配置文件扩展名
    configfile = form.configfile.data
    if configfile:
        if configfile.filename.lower().endswith('.ini'):
            configfile.filename = current_app.config['CONFIG_NAME']
        else:
            errors.append("Invalid Config file, only ini accepted")
    # 测试套扩展名
    for testsuite in filter(None, form.testsuites.raw_data):
        if not testsuite.filename.lower().endswith('.xlsx'):
            errors.append("Invalid TestSuites only xlsx accepted")
            break
    # 测试文件扩展名
    for testfile in filter(None, form.testfiles.raw_data):
        if testfile.filename == '' or (testfile.filename.lower().rsplit('.', maxsplit=1)[-1] not in current_app.config['TESTFILE_EXTENSIONS']):
            errors.append("Invalid TestFiles")
            break
    return errors


# 创建项目
def create_project(project, userid, mode):
    db = sqlitedb.connection
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
    db = sqlitedb.connection
    db.execute('UPDATE tb_project SET project=? WHERE uid=? AND pid=?', [
               projectname, userid, projectid])
    db.commit()


def rm_project(projectid, userid):
    db = sqlitedb.connection
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
    db = sqlitedb.connection
    cur = db.execute(
        'SELECT mode FROM tb_project WHERE uid=? AND pid=?', [userid, projectid])
    res = cur.fetchone()
    if res:
        # integer
        return res[0]


def set_projectstatus(userid, projectid, status):
    db = sqlitedb.connection
    db.execute('UPDATE tb_project SET status=? WHERE uid=? AND pid=?', [
               status, userid, projectid])
    db.commit()


def set_projectmode(userid, projectid, mode):
    db = sqlitedb.connection
    db.execute('UPDATE tb_project SET mode=? WHERE uid=? AND pid=?',
               [mode, userid, projectid])
    db.commit()


def runlocal(userid, projectid):
    r = subprocess.run([sys.executable, os.path.join(
        current_app.root_path, '..', 'run.py'), userid, projectid], stdout=subprocess.PIPE)
    if r.returncode:
        # error
        set_projectstatus(userid, projectid, 'Failing')
    else:
        set_projectstatus(userid, projectid, 'Passing')


def runremote(userid, projectid):
    r = subprocess.run([sys.executable, os.path.join(
        current_app.root_path, '..', 'sender.py'), userid, projectid], stdout=subprocess.PIPE)
    if r.returncode:
        # error
        set_projectstatus(userid, projectid, 'Failing')
    else:
        set_projectstatus(userid, projectid, 'Need confirmation')






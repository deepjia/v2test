"""Forms"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FileField, TextAreaField, RadioField
from wtforms.validators import InputRequired, EqualTo, Length


class LoginForm(FlaskForm):
    """登录表单"""
    username = StringField('Username', validators=[
                           InputRequired(message='Username required')])
    password = PasswordField('Password', validators=[
                             InputRequired(message='Password required')])
    submit = SubmitField('Login')
    reg = SubmitField('Register')


class RegForm(FlaskForm):
    """注册表单"""
    username = StringField('Username', validators=[InputRequired(
        message='Username required'), Length(min=3, max=25, message='Username should be 3-25 chars')])
    password = PasswordField('Password', validators=[InputRequired(
        message='Password required'), Length(min=3, max=30, message='Password should be 3-30 chars')])
    confirm = PasswordField('Confirm Password', validators=[InputRequired(
        message='Please confirm password'), EqualTo('password', message='Passwords mismatch')])
    submit = SubmitField('Register')
    cancel = SubmitField('Cancel')


class ProjectForm(FlaskForm):
    """项目表单"""
    projectname = StringField('Project Name', validators=[InputRequired(
        message='Project name required'), Length(min=4, max=25, message='Project name should be 4-25 chars')])
    testsuites = FileField('TestSuites')
    testfiles = FileField('TestFiles')
    configfile = FileField('Config File')
    configcontent = TextAreaField('Edit Config')
    mode = RadioField('Run Mode', choices=[('0', 'Local'), ('1', 'Remote')])
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel')

from . import db

class User(db.Model):
    __tablename__ = 'tb_user'
    id = db.Column(db.Interger, primary_key=True, autoincrement = True)
    username = db.Column(db.String(64),unique=True)
    password = db.Column(db.String(64))

    def __repr__(self):
        return '<User %r> ' % self.username


class Project(db.Model):
    __tablename__ = 'tb_project'
    id = db.Column(db.Interger, primary_key=True)
    projectname = db.Column(db.String(64))
    status = db.Column(db.String(64), server_default='Init')
    runmode = db.Column(db.Boolean, server_default=0)
    userid = db.Column(db.Interger)

    def __repr__(self):
        return '<Project %r> ' % self.projectname
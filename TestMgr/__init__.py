from flask import Flask,g
from flask_bootstrap import Bootstrap
#from flask_sqlalchemy import SQLAlchemy
from mgr_config import config
from .f_sqlite3 import SQLite3

bootstrap = Bootstrap()
#db = SQLAlchemy()
sqlitedb = SQLite3()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    sqlitedb.init_app
    #db.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
    
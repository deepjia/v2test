import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    TESTSUITE_DIR = 'TestSuites'
    TESTFILE_DIR = 'TestFiles'
    TESTREPORT_DIR = 'TestReports'
    TEMPLATE_DIR = 'templates'
    CONFIG_NAME = 'config.ini'
    TEMPLATE_NAME = 'template.zip'
    TEMPLATE_CONFIG = os.path.join(basedir, 'TestMgr', 'templates', 'config.ini')
    DOWNOAD = os.path.join(basedir, 'TestMgr', 'download')
    TESTFILE_EXTENSIONS = set(
        ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'log', 'sql', 'xlsx', 'csv', 'html', 'htm', 'py'])
    BOOTSTRAP_SERVE_LOCAL = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    #SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    #SQLALCHEMY_TRACK_MODIFICATIONS = False
    

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE = os.path.join(basedir, 'mgr_dev.db')
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'mgr_dev.db')


class ProductionConfig(Config):
    DATABASE = os.path.join(basedir, 'mgr.db')
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'mgr.db')


class TestingConfig(Config):
    TESTING = True
    DATABASE = os.path.join(basedir, 'mgr_test.db')
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'mgr_test.db')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
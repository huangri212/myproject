import os

# basedir = os.path.abspath(os.path.dirname(__file__))
basedir = "C:\\Users\\huanri\\PycharmProject\\myproject\\"


MAIL_SERVER = 'smtp.163.com'
MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
MAIL_USERNAME = '1034798224@qq.com'
MAIL_PASSWORD = 'kzksjiagaqplbbhb'
ADMINS = ['rih@hpe.com']
POSTS_PER_PAGE = 3


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = "sqlite:///C:\\Users\\huanri\\PycharmProject\\myproject\\app.db"
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
    SQLALCHEMY_TRACK_MODIFICATION = True
    POSTS_PER_PAGE = 3

    # MAIL_SERVER = os.environ.get('MAIL_SERVER')
    # MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    # MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    # MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    # ADMINS = ['rih@hpe.com']
    
 
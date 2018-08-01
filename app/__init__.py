from flask import Flask, url_for, request, render_template, g, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_openid import OpenID
from config import basedir, Config
from flask_migrate import Migrate
import os, logging
import logging
from logging.handlers import SMTPHandler
from flask_mail import Message
from flask_mail import Mail
from logging.handlers import RotatingFileHandler

# from config import Config

app = Flask(__name__)
FLASK_DEBUG = False

app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///C:\\Users\\huanri\\Documents\\myproject\\app.db"
db = SQLAlchemy(app)  # type: object
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
# oid = OpenID(app,os.path.join(basedir,'tmp'))\

if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
    # logging to a file #
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/myproject.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s:%(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')

from app import views, models
from app import errors

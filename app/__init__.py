import logging
import os
from logging.handlers import RotatingFileHandler
from logging.handlers import SMTPHandler

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel
from flask_babel import lazy_gettext as _l
from flask import request
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
FLASK_DEBUG = False
mail = Mail(app)
app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///C:\\Users\\huanri\\PycharmProjects\\myproject\\app.db"
db = SQLAlchemy(app)  # type: object
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
login = LoginManager(app)
login.login_view = 'login'
login.login_message = _l('Please log in to access this page.')
login.login_view = 'login'
moment = Moment(app)
babel = Babel(app)


@babel.localeselector
def get_locale():
    # return request.accept_languages.best_match(app.config['LANGUAGES'])
    return 'en'


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
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/myproject.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s:%(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    # app.logger.info('Microblog startup')

from app import views, models
from app import errors

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
import flask_whooshalchemyplus
from flaskext.markdown import Markdown




app = Flask(__name__, static_folder='static')
app.config.from_pyfile('configs.py')
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_message = '要访问该页面请您登录!'
login_manager.needs_refresh_message = '请验证后再登录!'
login_manager.login_view = 'login'
Markdown(app)
Bootstrap(app)
mail = Mail(app)
flask_whooshalchemyplus.init_app(app)

from app import models, views

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler

    file_handler = RotatingFileHandler('logs/myblog.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info(u'程序启动:')
    app.logger.debug(u'调试信息:')
    app.logger.warning(u'警告信息:')
    app.logger.error(u'错误信息:')
    app.logger.critical(u'严重错误:')

if __name__ == '__main__':
    app.run(host='0.0.0.0')

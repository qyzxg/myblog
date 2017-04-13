from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
import flask_whooshalchemyplus
from flaskext.markdown import Markdown

bootstrap = Bootstrap()
mail = Mail()
db = SQLAlchemy()
login_manager = LoginManager()

login_manager.session_protection = 'strong'
login_manager.login_message = '要访问该页面请您登录!'
login_manager.needs_refresh_message = '请验证后再登录!'
login_manager.login_view = 'auth.login'


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('configs.py')
    bootstrap.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    Markdown(app)
    flask_whooshalchemyplus.init_app(app)

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

    from .admin import admin
    app.register_blueprint(admin)

    from .public import public
    app.register_blueprint(public)

    from .auth import auth
    app.register_blueprint(auth)

    from .profile import profile
    app.register_blueprint(profile)

    return app



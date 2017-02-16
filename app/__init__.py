from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_pagedown import PageDown
from flask_mail import Mail

app = Flask(__name__,static_folder='static')
app.config.from_pyfile('configs.py')
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_message = '要访问该页面请您登录!'
login_manager.needs_refresh_message = '请验证后再登录!'
login_manager.login_view = 'login'
pagedown = PageDown()
pagedown.init_app(app)
Bootstrap(app)
mail = Mail(app)





from app import models, views

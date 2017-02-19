#!/usr/bin/python
# -*- coding:utf-8 -*-
from os import path
SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:qyzxg@localhost:3306/blog'
SQLALCHEMY_TRACK_MODIFICATIONS= True

SQLALCHEMY_COMMIT_ON_TEARDOWN = True
SECRET_KEY = 'zAs5AVQp9sGo5bpf0LzNUVyyyOTYjh'
SECURITY_PASSWORD_SALT = 'qyzxg'


'''email'''

MAIL_SERVER = 'smtp.sina.com'
MAIL_PORT = 25
# MAIL_USE_TLS = False
# MAIL_USE_SSL = True
# MAIL_DEBUG : default app.debug
MAIL_USERNAME = 'qyzxg1314@sina.com'
MAIL_PASSWORD = '852000zxg'
MAIL_DEFAULT_SENDER = 'qyzxg1314@sina.com'

UPLOAD_FOLDER = r'static\avatar\avatar'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'])
BASE_PATH = path.abspath(path.dirname(__file__))

#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
from os import path

SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:qyzxg@localhost:3306/blog'
SQLALCHEMY_TRACK_MODIFICATIONS = True

SQLALCHEMY_COMMIT_ON_TEARDOWN = True
SECRET_KEY = 'zAs5AVQp9sGo5bpf0LzNUVyyyOTYjh'
SECURITY_PASSWORD_SALT = 'GPXYdKtqLDhpvr60yVwz'

'''email'''

MAIL_SERVER = 'smtp.sina.com'
MAIL_PORT = 25
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

'''upload'''
UPLOAD_FOLDER = r'static\avatar\avatar'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'])
BASE_PATH = path.abspath(path.dirname(__file__))

'''text research'''
WHOOSH_BASE = 'search'
MAX_SEARCH_RESULTS = 50

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'

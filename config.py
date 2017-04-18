#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
from os import path


class Config:
    # 数据库
    SECRET_KEY = 'zAs5AVQp9sGo5bpf0LzNUVyyyOTYjh'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    FLASKY_SLOW_DB_QUERY_TIME = 0.5

    # 邮件
    MAIL_SERVER = 'smtp.sina.com'
    MAIL_PORT = 25
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    SECURITY_PASSWORD_SALT = 'GPXYdKtqLDhpvr60yVwz'

    # 缓存和异步
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'

    # 搜索
    WHOOSH_BASE = 'search'
    MAX_SEARCH_RESULTS = 50
    PROPAGATE_EXCEPTIONS = True

    # 文件上传
    UPLOAD_FOLDER = r'app\static\avatar\avatar'
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'])
    BASE_PATH = path.abspath(path.dirname(__file__))


class DevelopmentConfig(Config):#mysqlconnector
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:qyzxg@localhost:3306/blog'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:qyzxg@localhost:3306/test_blog'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:qyzxg@localhost:3306/blog'


config = {
    'development': DevelopmentConfig,
    'test': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}

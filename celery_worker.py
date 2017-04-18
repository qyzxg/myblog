#!/usr/bin/python
# -*- coding:utf-8 -*-

# 在celery_worker.py目录下运行   celery worker -A celery_worker.celery --loglevel=info

from app import create_app,celery
from celery import platforms

platforms.C_FORCE_ROOT = True
app = create_app('default')
app.app_context().push()

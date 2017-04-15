#!/usr/bin/python
# -*- coding:utf-8 -*-

#在celery_worker.py目录下运行   celery worker -A celery_worker.celery --loglevel=info

from app import celery, create_app
from celery import platforms


platforms.C_FORCE_ROOT = True   #加上这一行
app = create_app()
app.app_context().push()
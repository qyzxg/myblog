#!/usr/bin/python
# -*- coding:utf-8 -*-
from datetime import timedelta
from kombu import Queue
from celery.schedules import crontab


class MyRouter(object):
    def route_for_task(self, task, args=None, kwargs=None):
        if task.startswith('sche'):
            return {'queue': 'schedule'}
        elif task.startswith('cron'):
            return {'queue': 'crontab'}
        else:
            return {'queue': 'default'}


BROKER_POOL_LIMIT = 10
BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
CELERY_ENABLE_UTC = True
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'
CELERY_TASK_RESULT_EXPIRES = 3600
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']

CELERYBEAT_SCHEDULE = {
    'sche_write_info': {
        'task': 'sche_write_info',
        'args': (r'/var/log/nginx/access.log', r'/var/log/nginx/access.txt'),
        'schedule': timedelta(seconds=900)
    },
    'sche_sort_score': {
        'task': 'sche_sort_score',
        'schedule': timedelta(seconds=1800)
    },
    'cron_crawl_post': {
        'task': 'cron_crawl_post',
        'schedule': crontab(hour=22, minute=55)
    }
}

CELERY_QUEUES = (
    Queue(name='schedule', routing_key='schedule'),
    Queue(name='crontab', routing_key='crontab'),
    Queue(name='default', routing_key='default')
)

CELERY_DEFAULT_QUEUE = 'default'
CELERY_DEFAULT_EXCHANGE_TYPE = 'topic'
CELERY_DEFAULT_ROUTING_KEY = 'default'
CELERY_ROUTES = (MyRouter(),)

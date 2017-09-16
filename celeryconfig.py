#!/usr/bin/python
# -*- coding:utf-8 -*-
from datetime import timedelta

BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
CELERY_ENABLE_UTC = True,
# LOG_FILE = r'/var/log/celery/worker.log',
# CELERYBEAT_LOG_FILE = r'/var/log/celery/beat.log',
CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']
CELERYBEAT_SCHEDULE = {
    'write_info': {
        'task': 'write_info',
        'args': (r'/var/log/nginx/access.log', r'/var/log/nginx/access.txt'),
        'schedule': timedelta(seconds=900)
    },
    'sort_score': {
        'task': 'sort_score',
        'schedule': timedelta(seconds=1800)
    },
    # 'get_post': {
    #     'task': 'sort_score',
    #     'schedule': timedelta(seconds=100)
    # }
}

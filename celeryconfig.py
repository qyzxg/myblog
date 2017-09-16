#!/usr/bin/python
# -*- coding:utf-8 -*-
from datetime import timedelta
from kombu import Exchange, Queue


# class MyRouter(object):
#     def route_for_task(self, task, args=None, kwargs=None):
#         if task == 'app.tasks.celery_tasks.get_post_img' or 'app.tasks.celery_tasks.send_email':
#             return {
#                 'queue': 'default'
#             }
#         elif task == 'sort_score' or 'write_info':
#             return {
#                 "queue": "schedule"
#             }
#         else:
#             return {
#                 "queue": "timing"
#             }


BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
CELERY_ENABLE_UTC = True
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_RESULT_EXPIRES = 3600
CELERY_TIMEZONE = 'Asia/Shanghai'
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
    #     'task': 'get_post',
    #     'schedule': timedelta(seconds=100)
    # }
}

# default_exchange = Exchange('default', type='direct')
# host_exchange = Exchange('crontab', type='direct')
#
# CELERY_QUEUES = (
#                     Queue('default', default_exchange, routing_key='default'),
#                     Queue('schedule', host_exchange, routing_key='crontab.schedule'),
#                     Queue('timing', host_exchange, routing_key='crontab.timing'),
#                 ),

# CELERY_DEFAULT_QUEUE = 'default'
# CELERY_DEFAULT_EXCHANGE = 'default'
# CELERY_DEFAULT_ROUTING_KEY = 'default'
# CELERY_ROUTES = (MyRouter(),)

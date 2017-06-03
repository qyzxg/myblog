#!/usr/bin/python
# -*- coding:utf-8 -*-
from datetime import timedelta


class CeleryConfig:
    CELERYBEAT_SCHEDULE = {
        'every-minute': {
            'task': 'printnum',
            # 'schedule': crontab(minute='*/1'),
            # 'args': (1,2),
            'schedule': timedelta(seconds=5)
        },
        'every-minute-hahaha': {
            'task': 'hahaha',
            # 'schedule': crontab(minute='*/1'),
            # 'args': (1,2),
            'schedule': timedelta(seconds=5)
        },
    }

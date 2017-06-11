#!/usr/bin/python
# -*- coding:utf-8 -*-

from .. import celery, mail, create_app, db
from flask_mail import Message
import re
from threading import Thread, Timer
from time import sleep
from ..models import LogInfo, Post
import datetime
import subprocess
import signal
import os
import time


@celery.task
def send_email(to, subject, template):
    app = create_app('default')
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    with app.app_context():
        mail.send(msg)


# def send_async_email(app, msg):
#     with app.app_context():
#         mail.send(msg)
#
#
# def send_email(to, subject, template):
#     app = create_app('default')
#     msg = Message(
#         subject,
#         recipients=[to],
#         html=template,
#         sender=app.config['MAIL_DEFAULT_SENDER']
#     )
#     thr = Thread(target=send_async_email, args=[app, msg])
#     thr.start()


@celery.task
def get_post_img(post):
    reg = r'<img src="(.*?)".*?/>'
    imgs = re.compile(reg)
    img_list = imgs.findall(post.body)
    if img_list:
        img = ''.join(img_list[0])
        return img
    else:
        return None


# class Scheduler(object):
#     '''实现定时任务'''
#
#     def __init__(self, sleep_time, func):
#         self.sleep_time = sleep_time
#         self.func = func
#         self._t = None
#
#     def start(self):
#         if self._t is None:
#             self._t = Timer(self.sleep_time, self._run)
#             self._t.start()
#         else:
#             raise Exception("This timer is already running!")
#
#     def _run(self):
#         self.func()
#         self._t = Timer(self.sleep_time, self._run)
#         self._t.start()
#
#     def stop(self):
#         if self._t is not None:
#             self._t.cancel()
#             self._t = None


# class ReadLog():
#     def __init__(self, logfile=r'E:\MyProject\deploy\access.log',
#                  seekfile=r'E:\MyProject\deploy\access.seek'):
#         self.logfile = logfile
#         self.seekfile = seekfile
#
#     def _write_seek(self, seek=0):
#         # 写入当前的seek位置
#         with open(self.seekfile, 'w+', encoding='utf-8') as file:
#             file.write(str(seek))
#
#     def _read_seek(self):
#         # 读取文件的seek位置
#         with open(self.seekfile, 'r', encoding='utf-8') as file:
#             result = file.read()
#             if result:
#                 return int(result)
#         return 0
#
#     def read_content(self):
#         app = create_app('default')
#         file_seek = self._read_seek()
#         with open(self.logfile, 'r', encoding='utf-8') as file:
#             if len(file.readlines()) <= 5:
#                 self._write_seek(0)  # 当log文件被rotate后,将指针位置指向文件开头
#             else:
#                 file.seek(file_seek, 0)
#             while True:
#                 _row = file.readline()
#                 if _row:
#                     file_seek += len(_row)
#                     self._write_seek(file_seek)
#                     line = _row.split()
#                     try:
#                         ip = line[0]
#                         time_r = datetime.datetime.strptime(line[3][1:], '%d/%b/%Y:%H:%M:%S')
#                         status_code = int(line[5])
#                         length = line[6]
#                         url = line[7]
#                         req_time = float(line[10])
#                         res_time = float(line[11])
#                         loginfo = LogInfo(ip=ip, time_r=time_r, status_code=status_code,
#                                           length=length, url=url, req_time=req_time,
#                                           res_time=res_time, time_stamp=int(time.time()))
#                         with app.app_context():
#                             db.session.add(loginfo)
#                             db.session.commit()
#                     except:
#                         pass
#                 else:
#                     break


@celery.task(name='write_info')
def write_info(logfile, seekfile):
    app = create_app('default')
    file_seek = read_seek(seekfile)
    with open(logfile, 'r', encoding='utf-8') as file:
        if len(file.readlines()) <= 10:
            write_seek(seekfile, 0)  # 当log文件被rotate后,将指针位置指向文件开头
        else:
            file.seek(file_seek, 0)
        while True:
            _row = file.readline()
            if _row:
                file_seek += len(_row)
                write_seek(seekfile, file_seek)
                line = _row.split()
                try:
                    ip = line[0]
                    time_r = datetime.datetime.strptime(line[3][1:], '%d/%b/%Y:%H:%M:%S')
                    status_code = int(line[5])
                    length = line[6]
                    url = line[7]
                    req_time = float(line[10])
                    res_time = float(line[11])
                    loginfo = LogInfo(ip=ip, time_r=time_r, status_code=status_code,
                                      length=length, url=url, req_time=req_time,
                                      res_time=res_time, time_stamp=int(time.time()))
                    with app.app_context():
                        db.session.add(loginfo)
                        db.session.commit()
                except:
                    pass
            else:
                break


def write_seek(seekfile, seek=0):
    # 写入当前的seek位置
    with open(seekfile, 'w+', encoding='utf-8') as file:
        file.write(str(seek))


def read_seek(seekfile):
    # 读取文件的seek位置
    with open(seekfile, 'r', encoding='utf-8') as file:
        result = file.read()
        if result:
            return int(result)
        return 0


@celery.task(name='sort_score')
def sort_score():
    app = create_app('default')
    with app.app_context():
        posts = Post.query.all()
        for post in posts:
            post.sort_score = post.cal_sort_score()

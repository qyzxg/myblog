#!/usr/bin/python
# -*- coding:utf-8 -*-
import requests
from abc import ABCMeta, abstractmethod
from .. import create_app, db
from ..models import Post
import datetime
from ..shares import UploadToQiniu, choice_img


class BaseCrawler(metaclass=ABCMeta):
    def __init__(self):
        self.site = None
        self.timeout = 30
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
                          '60.0.3112.113 Safari/537.36'
        }
        self.today = datetime.datetime.today().strftime('%Y-%m-%d')

    def fetch_page(self, url, data=None, headers=None, timeout=None):
        try:
            timeout = timeout or self.timeout
            headers = headers or self.headers
            if data is None:
                r = self.session.get(url=url, timeout=timeout, headers=headers)
            else:
                r = self.session.post(url=url, data=data, timeout=timeout, headers=headers)
        except Exception as e:
            print(str(e))
        else:
            return r

    def login(self):
        cookies = self._login()
        self.session.cookies = cookies

    def _login(self):
        pass

    def parser(self):
        pass

    def save(self, title, body, style='转载', category='Python 进阶', post_img=choice_img()):
        app = create_app('default')
        with app.app_context():
            post = Post(title=title,
                        body=body,
                        style=style,
                        category=category,
                        author_id=1,
                        post_img=post_img,
                        created=datetime.datetime.now(),
                        source=self.site)
            db.session.add(post)
            db.session.commit()

    def is_today(self, s):
        return s == datetime.datetime.now().strftime('%Y-%m-%d')

    def start(self):
        pass

    def upload_img(self, file_name, file, prefix, domian_name='https://static.51qinqing.com'):
        u = UploadToQiniu(file, prefix, mark=True)
        ret, info = u.upload_web(prefix + file_name, file)
        key = ret['key']
        url = domian_name + '/' + key
        return url

    @abstractmethod
    def parse(self):
        pass

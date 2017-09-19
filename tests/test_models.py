#!/usr/bin/python
# -*- coding:utf-8 -*-
import unittest
from app import create_app, db
from app.models import User
import datetime


class ModelTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app('test')
        self.app_ctx = self.app.app_context()
        self.app_ctx.push()
        db.drop_all()
        db.create_all()

    def tearDown(self):
        self.app_ctx.pop()

    def test_insert_user(self):
        user = User(username='qyzxg',
                    email='541020258@qq.com',
                    password='123456',
                    created_at=datetime.datetime.now(),
                    updated_at=datetime.datetime.now(),
                    last_login=datetime.datetime.now(),
                    role=1)
        user.set_password(user.password)
        db.session.add(user)
        db.session.commit()

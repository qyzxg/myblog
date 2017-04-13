#!/usr/bin/python
# -*- coding:utf-8 -*-

from flask import Blueprint


auth = Blueprint('auth', __name__, url_prefix='/auth')


from . import views, forms
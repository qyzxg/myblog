#!/usr/bin/python
# -*- coding:utf-8 -*-

from flask import Blueprint

admin = Blueprint('admin', __name__)

from . import views, forms

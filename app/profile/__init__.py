#!/usr/bin/python
# -*- coding:utf-8 -*-

from flask import Blueprint

profile = Blueprint('profile', __name__)

from . import views
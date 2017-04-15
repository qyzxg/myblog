#!/usr/bin/python
# -*- coding:utf-8 -*-

from flask import jsonify, request, current_app, url_for
from . import api
from ..models import User, Post

@api.route('/users/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())


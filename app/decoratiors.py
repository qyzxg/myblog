#!/usr/bin/python
# -*- coding:utf-8 -*-

from functools import wraps
from flask_login import current_user
from flask import flash


def admin_permission_requied(view_func):
    @wraps
    def wraper(*args, **kwargs):
        # 查询用户的角色
        roles = current_user.role
        if roles == 1 and current_user.is_valid == 1:
            return view_func(*args, **kwargs)
        flash('您还没有权限进行该操作')

    return wraper

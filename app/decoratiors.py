#!/usr/bin/python
# -*- coding:utf-8 -*-

from functools import wraps
from flask_login import current_user
from flask import flash, redirect, url_for, request


def admin_required(f):
    @wraps(f)
    def view_function(*args, **kwargs):
        if not current_user.role == 1:
            flash('您没有管理员权限!')
            return redirect(url_for('public.index'))
        return f(*args, **kwargs)

    return view_function

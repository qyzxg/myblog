#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class NewCategory(FlaskForm):
    name = StringField('分类', validators=[DataRequired("分类不允许为空")])
    submit = SubmitField('添加')

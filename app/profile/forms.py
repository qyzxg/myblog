#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Regexp, NumberRange, URL


class UserInfoForm(FlaskForm):
    age = IntegerField('年龄', validators=[NumberRange(min=12, max=80, message='年龄必须在12-80之间'),
                                         Regexp(r'^[0-9]{2}$', 0, u'年龄只能用数字')],
                       render_kw={'class': "form-control"},
                       _name="age"
                       )

    gender = SelectField('性别', validators=[DataRequired()], render_kw={'class': "form-control", "required": "required"},
                         _name="gender"
                         )
    education = SelectField('学历', render_kw={'class': "form-control"}, _name="education", )
    graduated = SelectField('学校', render_kw={'class': "form-control"}, _name="graduated"
                            )
    industry = SelectField(u'行业', render_kw={'class': "form-control"}, _name="industry"
                           )
    company = StringField(u'公司', render_kw={'class': "form-control"}, _name="company")
    position = SelectField(u'职位', render_kw={'class': "form-control"}, _name="position"
                           )
    language = SelectField(u'语言', render_kw={'class': "form-control"},
                           _name="language"
                           )
    website = StringField(u'网站', validators=[URL(message=u'URL格式不正确')], render_kw={'class': "form-control"},
                          _name="website"
                          )
    submit = SubmitField(render_kw={'class': "btn btn-info", 'value': '提交'})

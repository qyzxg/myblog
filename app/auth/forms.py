#!/usr/bin/python
# -*- coding:utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError


class LoginForm(FlaskForm):
    username = StringField(label='用户名', validators=[DataRequired()],
                           render_kw={'class': "form-control", "required": "required"},
                           _name="username", description="请输入用户名", default="请输入用户名"
                           )
    password = PasswordField(label='密码', validators=[DataRequired()],
                             render_kw={'class': "form-control", "required": "required"},
                             _name="password", description="请输入密码"
                             )
    remember_me = BooleanField(label='记住我')
    submit = SubmitField(render_kw={'class': "btn btn-info btn-block"})

    def get_user(self):
        from ..models import User
        return User.query.filter_by(username=self.data['username']).first()


class RegistForm(FlaskForm):
    username = StringField(label='用户名', validators=[DataRequired(), Length(min=5, max=16, message='用户名必须大于5位! ')],
                           render_kw={'class': "form-control", "required": "required"},
                           _name="username", description="请输入用户名", default="请输入用户名"
                           )

    password = PasswordField(label='密码', validators=[DataRequired(), Length(min=6, max=16, message='密码必须大于6位! ')],
                             render_kw={'class': "form-control", "required": "required"},
                             _name="password", description="请输入密码"
                             )
    confirm = PasswordField(label='确认密码', validators=[DataRequired(), EqualTo('password', message='两次输入的密码不一样! ')],
                            render_kw={'class': "form-control", "required": "required"},
                            _name="qrpassword", description="请再一次输入密码")
    email = StringField(label='邮箱', validators=[DataRequired(), Email(message='请输入正确的邮箱! ')],
                        render_kw={'class': "form-control", "required": "required"},
                        _name="email", description="请输入邮箱", default="请输入邮箱"
                        )
    submit = SubmitField(render_kw={'class': "btn btn-info btn-block"})

    def validate_username(self, field):
        from ..models import User
        data = field.data
        if User.query.filter_by(username=data).first():
            raise ValidationError('用户名已存在')
        return data

    def validate_email(self, field):
        from ..models import User
        data = field.data
        if User.query.filter_by(email=data).first():
            raise ValidationError('邮箱已存在')
        return data


class AuthEmail(FlaskForm):
    email = StringField('email', validators=[DataRequired("请输入您注册时使用的邮箱")],
                        render_kw={'class': "form-control", "required": "required"})

    def get_user(self):
        from ..models import User
        return User.query.filter_by(email=self.data['email']).first()


class ResetPassword(FlaskForm):
    password = PasswordField('password', validators=[DataRequired(), Length(min=6, max=16, message='密码必须大于6位! ')],
                             render_kw={'class': "form-control", "required": "required"})
    confirm = PasswordField('confirm', validators=[DataRequired(), EqualTo('password', message='两次输入的密码不一样! ')],
                            render_kw={'class': "form-control", "required": "required"})

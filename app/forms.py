#!/usr/bin/python
# -*- coding:utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User
from flaskckeditor import CKEditor

from flask_pagedown.fields import PageDownField


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
        from app.models import User
        data = field.data
        if User.query.filter_by(username=data).first():
            raise ValidationError('用户名已存在')
        return data

    def validate_email(self, field):
        from app.models import User
        data = field.data
        if User.query.filter_by(email=data).first():
            raise ValidationError('邮箱已存在')
        return data


class PostForm(FlaskForm, CKEditor):
    title = StringField(label="标题", validators=[DataRequired(),
                                                Length(min=5, max=50, message='标题必须字数在5与20之间!')],
                        render_kw={"required": "required"})
    style = SelectField('类型', coerce=str)
    category = SelectField('分类', coerce=str)
    body = TextAreaField(label="正文", validators=[DataRequired(),
                                                 Length(min=10, message='文章内容必须大于10个字!')],
                         render_kw={"required": "required"})
    submit = SubmitField('发表', render_kw={'class': "btn btn-info btn-block"})


class CommentForm(FlaskForm):
    body = PageDownField(label='评论', validators=[DataRequired(),
                                                 Length(min=5, message='评论内容必须大于5个字!')],
                         render_kw={"required": "required"})
    submit = SubmitField(render_kw={'class': "btn btn-info btn-block"})


class AvatarForm(FlaskForm):
    avatar = FileField(label='图像', validators=[DataRequired("请选择一张图片")])


class NewCategory(FlaskForm):
    name = StringField('分类', validators=[DataRequired("分类不允许为空")])
    submit = SubmitField('添加')

class SearchForm(FlaskForm):
    search = StringField('search', validators=[DataRequired("请输入一个关键词")])
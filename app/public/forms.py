#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length


class PostForm(FlaskForm):
    title = StringField(label="标题", validators=[DataRequired(message='标题字数必须在5与60之间!'),
                                                Length(min=5, max=60, message='标题字数必须在5与60之间!')],
                        render_kw={"required": "required"})
    style = SelectField(label='类型', coerce=str)
    category = SelectField(label='分类', coerce=str)
    tags = StringField(label='文章标签')
    body = TextAreaField(label="正文", validators=[DataRequired(message='文章内容必须大于10个字!'),
                                                 Length(min=10, message='文章内容必须大于10个字!')],
                         )
    is_public = BooleanField(label='是否公开', render_kw={'checked': 'checked'})
    submit = SubmitField(label='发表', render_kw={'class': "btn btn-info btn-block"})


class CommentForm(FlaskForm):
    body = TextAreaField(label='评论', validators=[DataRequired(message='评论内容必须大于5个字!'),
                                                 Length(min=5, message='评论内容必须大于5个字!')],
                         render_kw={"required": "required"})
    submit = SubmitField(render_kw={'class': "btn btn-info btn-block"})


class SearchForm(FlaskForm):
    search = StringField(label='search', validators=[DataRequired("请输入一个关键词")])

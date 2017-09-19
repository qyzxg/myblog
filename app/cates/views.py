#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask import render_template
from . import cates
from ..models import Post, Tag
from .. import cache
from ..shares import do_pagination


@cache.cached(timeout=60, key_prefix='view_%s', unless=None)
@cates.route('/posts/<cate>/', methods=['GET'])
def get_cates(cate):
    query = Post.query.filter(Post.is_public == 1).order_by(Post.read_times.desc()).filter_by(category=cate)
    pagination, posts = do_pagination(query)
    total = len(Post.query.filter(Post.is_public == 1).filter_by(category=cate).all())
    return render_template('cates/get_cates.html',
                           posts=posts, pagination=pagination,
                           title='所有分类为%s的文章' % cate, total=total,
                           cate=cate,
                           )


@cache.cached(timeout=60, key_prefix='view_%s', unless=None)
@cates.route('/tags/<tag>/', methods=['GET'])
def get_tags(tag):
    tag_ = Tag.query.filter_by(name=tag).first()
    query = tag_.posts.filter(Post.is_public == 1)
    pagination, posts = do_pagination(query)
    total = len(query.all())
    return render_template('cates/get_tags.html', title='标签有%s的文章' % tag,
                           posts=posts, pagination=pagination, total=total,
                           tag=tag)

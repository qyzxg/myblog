#!/usr/bin/python
# -*- coding:utf-8 -*-

from flask import render_template, request
from . import cates
from ..models import Post, Tag
from .. import cache


@cache.cached(timeout=60, key_prefix='view_%s', unless=None)
@cates.route('/posts/<cate>/',methods=['GET'])
def get_cates(cate):
    page_index = request.args.get('page', 1, type=int)
    query = Post.query.filter(Post.is_public==1).order_by(Post.read_times.desc()).filter_by(category=cate)
    pagination = query.paginate(page_index, per_page=10, error_out=False)
    posts = pagination.items
    total = len(Post.query.filter(Post.is_public==1).filter_by(category=cate).all())
    return render_template('cates/get_cates.html',
                           posts=posts, pagination=pagination,
                           title='所有分类为%s的文章' % cate, total=total,
                           cate=cate,
                           )


@cache.cached(timeout=60, key_prefix='view_%s', unless=None)
@cates.route('/tags/<tag>/', methods=['GET'])
def get_tags(tag):
    page_index = request.args.get('page', 1, type=int)
    tag_ = Tag.query.filter_by(name=tag).first()
    query = tag_.posts.filter(Post.is_public==1)
    pagination = query.paginate(page_index, per_page=10, error_out=False)
    posts = pagination.items
    total = len(query.all())
    return render_template('cates/get_tags.html', title='标签有%s的文章' % tag,
                           posts=posts, pagination=pagination, total=total,
                           tag=tag)

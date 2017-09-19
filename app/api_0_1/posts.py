#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask import jsonify, request, url_for
from ..models import Post
from . import api
from ..shares import do_pagination


@api.route('/posts/')
def get_posts():
    page = request.args.get('page', 1, type=int)
    query = Post.query
    pagination, posts = do_pagination(query)
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page - 1, _external=True)
    next_ = None
    if pagination.has_next:
        next_ = url_for('api.get_posts', page=page + 1, _external=True)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next_,
        'count': pagination.total
    })


@api.route('/posts/<int:id_>')
def get_post(id_):
    post = Post.query.get_or_404(id_)
    return jsonify(post.to_json())

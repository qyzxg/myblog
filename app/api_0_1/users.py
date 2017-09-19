#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask import jsonify, request, url_for
from . import api
from ..models import User, Post
from ..shares import do_pagination


# @api.route('/users/')
# def get_users():
#     users = User.query.all()
#     return jsonify(users.to_json())


@api.route('/users/<int:id_>/')
def get_user(id_):
    user = User.query.get_or_404(id_)
    return jsonify(user.to_json())


@api.route('/users/<int:id_>/posts/')
def get_user_posts(id_):
    user = User.query.get_or_404(id_)
    page = request.args.get('page', 1, type=int)
    query = Post.query.filter_by(author_id=user.id).order_by(Post.created.desc())
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


@api.route('/users/<int:id_>/timeline/')
def get_user_collected_posts(id_):
    user = User.query.get_or_404(id_)
    page = request.args.get('page', 1, type=int)
    query = user.collected_posts()
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

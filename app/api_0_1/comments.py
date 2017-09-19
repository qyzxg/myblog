#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask import jsonify, request, url_for
from ..models import Post, Comment
from . import api
from ..shares import do_pagination


@api.route('/comments/')
def get_comments():
    query = Comment.query.order_by(Comment.created.desc())
    page = request.args.get('page', 1, type=int)
    pagination, comments = do_pagination(query)
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_comments', page=page - 1, _external=True)
    next_ = None
    if pagination.has_next:
        next_ = url_for('api.get_comments', page=page + 1, _external=True)
    return jsonify({
        'posts': [comment.to_json() for comment in comments],
        'prev': prev,
        'next': next_,
        'count': pagination.total
    })


@api.route('/comments/<int:id_>/')
def get_comment(id_):
    comment = Comment.query.get_or_404(id_)
    return jsonify(comment.to_json())


@api.route('/posts/<int:id_>/comments/')
def get_post_comments(id_):
    post = Post.query.get_or_404(id_)
    page = request.args.get('page', 1, type=int)
    query = Comment.query.filter_by(post_id=post.id).order_by(Comment.created.desc())
    pagination, comments = do_pagination(query)
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_comments', page=page - 1, _external=True)
    next_ = None
    if pagination.has_next:
        next_ = url_for('api.get_comments', page=page + 1, _external=True)
    return jsonify({
        'posts': [comment.to_json() for comment in comments],
        'prev': prev,
        'next': next_,
        'count': pagination.total
    })

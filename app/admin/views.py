#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
import time
from .. import db,cache
from . import admin
from ..models import User, Post, Comment, Categories
from .forms import NewCategory
from collections import OrderedDict


@cache.memoize(timeout=86400, unless=None)#获取每天文章总数,一天获取一次
def get_m_post():
    n = get_c_month()
    b = get_m_days()
    lst = [
        Post.query.filter(Post.created.between('2017-%s-%d 0:0:0' % (n, i), '2017-%s-%d 0:0:0' % (n, (i + 1)))).count()
        for
        i in range(1, b)]
    return lst


@cache.memoize(timeout=3600, unless=None)#获取文章分类,一小时一次
def get_a_cate():
    lst = [str(a.name) for a in Categories.query.all()]
    return lst

@cache.memoize(timeout=3600, unless=None)#获取文章分类,一小时一次
def get_a_cates():
    lst = [Post.query.filter_by(category=i).count() for i in get_a_cate()]
    return lst

@cache.memoize(timeout=86400, unless=None)#获取每天用户注册数,一天获取一次
def get_m_user():
    n = get_c_month()
    b = get_m_days()
    lst = [User.query.filter(
        User.created_at.between('2017-%s-%d 0:0:0' % (n, i), '2017-%s-%d 0:0:0' % (n, (i + 1)))).count() for
           i in range(1, b)]
    return lst

@cache.memoize(timeout=1296000, unless=None)#获取当前月份,15天一次
def get_c_month():
    return time.strftime('%m', time.localtime(time.time()))

@cache.memoize(timeout=1296000, unless=None)#获取当前月天数,15天一次
def get_m_days():
    n = get_c_month()
    if n in ['01', '03', '05', '07', '08', '10', '12']:
        a = 32
    else:
        a = 31
    return a


# 管理员后台首页
@admin.route('/admin')
@login_required
def admin_index():
    if current_user.role == 0:
        flash('您没有管理员权限!')
        return render_template('user/user_index.html', user=current_user,
                               title='用户首页')
    else:
        m = get_c_month()
        cat = get_a_cate()
        cats = get_a_cates()
        c = OrderedDict(zip(cats, cat))
        d = [{'value': k, 'name': v} for k, v in c.items()]
        x = list(range(1, get_m_days()))
        lt_post = get_m_post()
        lt_user = get_m_user()
        return render_template('admin/admin_index.html', title='管理员后台',
                               menu=0,
                               x=x, lt_post=lt_post,
                               lt_user=lt_user,
                               m=m, cat=cat, cats=cats, d=d
                               )


# 文章分类管理
@admin.route('/admin/new_category', methods=['POST', 'GET'])
@login_required
def new_category():
    categories = Categories.query.order_by(Categories.id)
    form = NewCategory()
    if form.validate_on_submit():
        category = Categories(
            name=form.name.data,
            name1=form.name.data
        )
        db.session.add(category)
        db.session.commit()
    return render_template('admin/new_category.html',
                           categories=categories,
                           form=form, menu=4, title='分类管理')


# 用户管理
@admin.route('/admin/users_manage', methods=['POST', 'GET'])
@login_required
def users_manage():
    page_index = request.args.get('page', 1, type=int)
    query = User.query.order_by(User.post_total.desc())
    pagination = query.paginate(page_index, per_page=10, error_out=False)
    users = pagination.items
    if current_user.role == 0:
        flash('您没有管理员权限!')
        return redirect(url_for('public.index'))
    else:
        return render_template('admin/users_manage.html',
                               users=users,
                               pagination=pagination,
                               title='用户管理', menu=1)


# 博客管理
@admin.route('/admin/blogs_manage', methods=['POST', 'GET'])
@login_required
def blogs_manage():
    page_index = request.args.get('page', 1, type=int)
    query = Post.query.order_by(Post.read_times.desc())
    pagination = query.paginate(page_index, per_page=10, error_out=False)
    posts = pagination.items
    if current_user.role == 0:
        flash('您没有管理员权限!')
        return redirect(url_for('public.index'))
    else:
        return render_template('admin/blogs_manage.html',
                               posts=posts,
                               pagination=pagination,
                               title='博客管理',
                               menu=2)


# 评论管理
@admin.route('/admin/comments_manage', methods=['POST', 'GET'])
@login_required
def comments_manage():
    page_index = request.args.get('page', 1, type=int)
    query = Comment.query.order_by(Comment.created.desc())
    pagination = query.paginate(page_index, per_page=10, error_out=False)
    comments = pagination.items
    if current_user.role == 0:
        flash('您没有管理员权限!')
        return redirect(url_for('public.index'))
    else:
        return render_template('admin/comments_manage.html',
                               comments=comments,
                               pagination=pagination,
                               title='评论管理',
                               menu=3)


# 博客删除
@admin.route('/admin/bolg_manage/<int:id>/')
@login_required
def blog_manage(id):
    if current_user.role == 0:
        flash('您没有管理员权限!')
        return redirect(url_for('public.index'))
    else:
        post = Post.query.filter_by(id=id).first()
        user = User.query.filter_by(id=post.author_id).first()
        user.post_total -= 1
        comments = Comment.query.filter_by(post_id=post.id).all()
        if post is None:
            flash('文章不存在!')
        if not current_user.is_authenticated:
            flash('请登录后再操作!')
        for i in comments:
            db.session.delete(i)
        db.session.delete(post)
        db.session.commit()
        user.post_total -= 1
        flash('文章删除成功!')
        return redirect(url_for('admin.blogs_manage'))


# 评论删除
@admin.route('/admin/comment_manage/<int:id>/')
@login_required
def comment_manage(id):
    if current_user.role == 0:
        flash('您没有管理员权限!')
        return redirect(url_for('public.index'))
    else:
        comment = Comment.query.filter_by(id=id).first()
        if comment is None:
            flash('评论不存在!')
        if not current_user.is_authenticated:
            flash('请登录后再操作!')
        db.session.delete(comment)
        db.session.commit()
        flash('评论删除成功!')
        return redirect(url_for('admin.comments_manage'))


# 用户登录管理
@admin.route('/admin/login_manage/<int:id>/<int:status>/<int:delete>')
@login_required
def login_manage(id, status, delete):
    if current_user.role == 0:
        flash('您没有管理员权限!')
        return redirect(url_for('public.index'))
    else:
        user = User.query.filter_by(id=id, is_valid=1).first()
        posts = Post.query.filter_by(author_id=user.id).all()
        comments = Comment.query.filter_by(author_id=user.id).all()
        if user is None:
            flash('用户不存在!')
        if not current_user.is_authenticated:
            flash('请登录后再操作!')
            # 设置用户状态
        if int(status) == 1:
            user.status = 1
        else:
            user.status = 0
        if int(delete) == 1:
            # 同时删除该用户的文章和评论
            for i in comments:
                db.session.delete(i)
            for j in posts:
                db.session.delete(j)
            db.session.delete(user)
            db.session.commit()
            flash('用户删除成功!')
        return redirect(url_for('admin.users_manage'))


# 角色管理
@admin.route('/admin/role_manage/<int:id>/<int:role>/')
@login_required
# @admin_permission_requied
def role_manage(id, role):
    if current_user.role == 0:
        flash('您没有管理员权限!')
        return redirect(url_for('public.index'))
    else:
        user = User.query.filter_by(id=id, is_valid=1).first()
        if user is None:
            flash('用户不存在!')
        if not current_user.is_authenticated:
            flash('请登录后再操作!')
            # 设置用户角色
        if int(role) == 1:
            user.role = 1
        else:
            user.role = 0
        return redirect(url_for('admin.users_manage'))

#!/usr/bin/python
# -*- coding:utf-8 -*-


from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
import datetime

from ..models import User, Post, Comment, Todo
from . import profile
from .. import db



# 用户资料页
@profile.route('/user/<username>', methods=['POST', 'GET'])
@login_required
def user_index(username):
    user = User.query.filter_by(username=username).first()
    if user == None:
        flash('不存在用户：' + username + '！')
        return redirect(url_for('public.index'))

    if user.id != current_user.id:
        flash('您没有权限访问该页面!')
        return redirect(url_for('public.index'))

    return render_template('profile/user_index.html', user=user,
                           title='%s的后台' % user.username,
                           menu=0)


@profile.route('/others/<username>', methods=['POST', 'GET'])
def others(username):
    page_index = request.args.get('page', 1, type=int)
    posts_ = Post.query.order_by(Post.comment_times.desc()).limit(5)
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('不存在用户：' + username + '！')
        return redirect(url_for('public.index'))
    else:
        query = Post.query.filter_by(author_id=user.id)
        pagination = query.paginate(page_index, per_page=10, error_out=False)
        posts = pagination.items

    return render_template('profile/others.html', user=user, posts=posts,
                           title='%s的资料' % user.username,
                           pagination=pagination, posts_=posts_,
                           menu=0)


@profile.route('/user/blogs_manage', methods=['POST', 'GET'])
@login_required
def user_blogs_manage():
    page_index = request.args.get('page', 1, type=int)

    query = Post.query.filter_by(author_id=current_user.id)

    pagination = query.paginate(page_index, per_page=10, error_out=False)

    posts = pagination.items

    return render_template('profile/blogs_manage.html',
                           posts=posts,
                           pagination=pagination,
                           title='博客管理',
                           menu=1)


@profile.route('/user/bolg_manage/<int:id>/')
@login_required
def user_blog_manage(id):
    post = Post.query.filter_by(id=id).first()
    user = User.query.filter_by(id=post.author_id).first()

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
    return redirect(url_for('profile.user_blogs_manage'))


@profile.route('/user/comments_manage', methods=['POST', 'GET'])
@login_required
def user_comments_manage():
    page_index = request.args.get('page', 1, type=int)

    query = Comment.query.filter_by(author_id=current_user.id)

    pagination = query.paginate(page_index, per_page=10, error_out=False)

    comments = pagination.items

    return render_template('profile/comments_manage.html',
                           comments=comments,
                           pagination=pagination,
                           title='评论管理',
                           menu=3)


@profile.route('/user/comment_manage/<int:id>/')
@login_required
def user_comment_manage(id):
    comment = Comment.query.filter_by(id=id).first()
    if comment is None:
        flash('评论不存在!')
    if not current_user.is_authenticated:
        flash('请登录后再操作!')
    db.session.delete(comment)
    db.session.commit()
    flash('评论删除成功!')
    return redirect(url_for('profile.user_comments_manage'))


@profile.route('/user/collects_manage', methods=['POST', 'GET'])
@login_required
def user_collects_manage():
    page_index = request.args.get('page', 1, type=int)
    user = current_user
    query = user.collected_posts()

    pagination = query.paginate(page_index, per_page=10, error_out=False)

    posts = pagination.items

    return render_template('profile/collects_manage.html',
                           posts=posts,
                           pagination=pagination,
                           title='收藏管理',
                           menu=2)

@profile.route('/user/followers_manage', methods=['POST', 'GET'])
@login_required
def user_followers_manage():
    page_index = request.args.get('page', 1, type=int)
    user = current_user
    query = user.followed_users()
    pagination = query.paginate(page_index, per_page=10, error_out=False)

    followers = pagination.items

    return render_template('profile/followers_manage.html',
                           followers=followers,
                           pagination=pagination,
                           title='好友管理',
                           menu=5)


@profile.route('/user/collect_manage/<int:id>/')
@login_required
def user_collect_manage(id):
    post = Post.query.get_or_404(id)
    current_user.uncollect(post)
    flash('取消收藏成功!')
    return redirect(url_for('profile.user_collects_manage'))

@profile.route('/user/follow_manage/<username>')
@login_required
def user_follower_manage(username):
    user = User.query.filter_by(username=username).first()
    current_user.unfollow(user)
    flash('取消关注成功!')
    return redirect(url_for('profile.user_followers_manage'))

@profile.route('/user/todos_manage', methods=['POST', 'GET'])
@login_required
def user_todos_manage():
    page_index = request.args.get('page', 1, type=int)
    query = Todo.query.filter_by(user_id=current_user.id).order_by(Todo.created.desc())
    pagination = query.paginate(page_index, per_page=10, error_out=False)
    todos = pagination.items
    return render_template('profile/todos_manage.html', todos=todos,
                           title='TODO管理', menu=4, pagination=pagination, )


@profile.route('/user/todo_add', methods=['POST', 'GET'])
@login_required
def todo_add():
    form = request.form
    content = form['content']
    if not content:
        flash('todo内容不能为空!')
        return redirect(url_for('profile.user_todos_manage'))
    else:
        todo = Todo(content=content, created=datetime.datetime.now(), user_id=current_user.id)
        db.session.add(todo)
        db.session.commit()
        flash('todo添加成功!')
    return redirect(url_for('profile.user_todos_manage'))


@profile.route('/user/todo_add/<int:id>')
@login_required
def todo_done(id):
    todo = Todo.query.get_or_404(id)
    todo.status = 1
    todo.finished = datetime.datetime.now()
    db.session.add(todo)
    db.session.commit()
    flash('状态修改成功!')
    return redirect(url_for('profile.user_todos_manage'))


@profile.route('/user/todo_undone/<int:id>')
@login_required
def todo_undone(id):
    todo = Todo.query.get_or_404(id)
    todo.status = 0
    todo.finished = None
    db.session.add(todo)
    db.session.commit()
    flash('状态修改成功!')
    return redirect(url_for('profile.user_todos_manage'))


@profile.route('/user/todo_dele/<int:id>')
@login_required
def todo_dele(id):
    todo = Todo.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    flash('todo删除成功!')
    return redirect(url_for('profile.user_todos_manage'))


# 收藏
@login_required
@profile.route('/collect/<int:id>')
def collect(id):
    post = Post.query.get_or_404(id)
    if current_user.is_authenticated:
        if current_user.collecting(post):
            flash('你已经收藏了这篇文章!')
            return redirect(url_for('public.details', id=post.id))
    else:
        flash('登录后才能收藏哦!')
        return redirect(url_for('public.details', id=post.id))

    current_user.collect(post)
    flash('收藏成功!')
    return redirect(url_for('public.details', id=post.id))



# 取消收藏
@login_required
@profile.route('/uncollect/<int:id>')
def uncollect(id):
    post = Post.query.get_or_404(id)
    if not current_user.collecting(post):
        flash('你没有收藏这篇文章!')
        return redirect(url_for('public.details', id=post.id))
    current_user.uncollect(post)
    flash('取消收藏成功!')
    return redirect(url_for('public.details', id=post.id))

#关注
@login_required
@profile.route('/follow/<username>')
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户 %s 没有找到.' % user.username)
        return redirect(url_for('public.index'))
    if user == current_user:
        flash('不能关注你自己')
        return redirect(url_for('profile.user_index', username=username))
    u = current_user.follow(user)
    if u is None:
        flash('不能关注 ' + user.username + '!')
        return redirect(url_for('profile.others', username=username))
    db.session.add(u)
    db.session.commit()
    flash('关注' + user.username + '成功')
    return redirect(url_for('profile.others', username=username))



@login_required
@profile.route('/unfollow/<username>')
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户 %s 没有找到.' % user.username)
        return redirect(url_for('public.index'))
    if user == current_user:
        flash('不能取消关注你自己')
        return redirect(url_for('profile.user_index', username=username))
    u = current_user.unfollow(user)
    if u is None:
        flash('不能取消关注 ' + user.username + '!')
        return redirect(url_for('profile.others', username=username))
    db.session.add(u)
    db.session.commit()
    flash('取消关注' + user.username + '成功')
    return redirect(url_for('profile.others', username=username))

#!/usr/bin/python
# -*- coding:utf-8 -*-


from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
import datetime

from ..models import User, Post, Comment, Todo, Message
from . import profile
from .. import db
from ..admin.views import get_c_month, get_m_days


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
    n = get_c_month()
    b = get_m_days()
    lst = [
        Post.query.filter_by(author_id=user.id).filter(
            Post.created.between('2017-%s-%d 0:0:0' % (n, i), '2017-%s-%d 0:0:0' % (n, (i + 1)))).count()
        for
        i in range(1, b)]
    x = list(range(1, get_m_days()))
    m = get_c_month()
    return render_template('profile/user_index.html', user=user,
                           title='%s的后台' % user.username,
                           menu=0, x=x, lst=lst, m=m)


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


@profile.route('/user/reward_manage')
@login_required
def user_reward_manage():
    user = current_user
    return render_template('profile/user_reward_manage.html',
                           user=user,title='打赏管理',meun=7)


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
    if request.method == "POST":
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

@profile.route('/collect/<int:id>')
@login_required
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

@profile.route('/uncollect/<int:id>')
@login_required
def uncollect(id):
    post = Post.query.get_or_404(id)
    if not current_user.collecting(post):
        flash('你没有收藏这篇文章!')
        return redirect(url_for('public.details', id=post.id))
    current_user.uncollect(post)
    flash('取消收藏成功!')
    return redirect(url_for('public.details', id=post.id))


# 关注

@profile.route('/follow/<username>')
@login_required
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



@profile.route('/unfollow/<username>')
@login_required
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



@profile.route('/send_message/', methods=['POST', 'GET'])
@login_required
def send_message():
    if request.method == 'POST':
        form = request.form
        content = form['content']
        sendto = form['sendto']
        user = User.query.filter_by(username=sendto).first()
        if sendto == '--请选择好友用户名--':
            flash('必须选择一个用户!')
            return redirect(url_for('profile.messages_manage'))
        if not content:
            flash('消息内容不能为空!')
            return redirect(url_for('profile.messages_manage'))

        message = Message(content=content,
                          sender=current_user,
                          sendto=user)
        db.session.add(message)
        db.session.commit()
        flash('消息发送成功!')
    return redirect(url_for('profile.messages_manage'))



@profile.route('/delete_message/<int:id>')
@login_required
def delete_message(id):
    message = Message.query.filter_by(id=id).first()
    if not message.confirmed:
        flash('对方还没有读过这条消息,不能删除!')
        return redirect(url_for('profile.messages_manage'))
    db.session.delete(message)
    db.session.commit()
    flash('消息删除成功!')
    return redirect(url_for('profile.messages_manage'))



@profile.route('/confirm_message/<int:id>')
@login_required
def confirm_message(id):
    message = Message.query.filter_by(id=id).first()
    message.confirmed = 1
    flash('消息状态更改成功!')
    return redirect(url_for('profile.messages_manage'))



@profile.route('/messages_manage')
@login_required
def messages_manage():
    user = current_user
    friends1 = user.followed_users()
    managers = User.query.filter_by(role=1).all()
    users = User.query.all()
    if current_user.role == 1:
        friends = users
    else:
        friends = list(managers) + list(friends1)
    unconfirmed_messages = Message.query.order_by(Message.created_at.desc()).filter_by(sendto=current_user).filter_by(
        confirmed=False).all()
    confirmed_messages = Message.query.order_by(Message.created_at.desc()).filter_by(sendto=current_user).filter_by(
        confirmed=True).all()
    sended_messages = Message.query.order_by(Message.created_at.desc()).filter_by(sender=current_user).all()
    sys_messages = Message.query.order_by(Message.created_at.desc()).filter_by(sendto=current_user).filter(
        User.role == 1).all()
    n_u = len(unconfirmed_messages)
    n_c = len(confirmed_messages)
    n_s = len(sended_messages)
    n_sy = len(sys_messages)
    return render_template('profile/messages_manage.html', menu=6, title='好友管理', friends=friends,
                           unconfirmed_messages=unconfirmed_messages,
                           confirmed_messages=confirmed_messages,
                           sended_messages=sended_messages,
                           n_u=n_u, n_c=n_c, n_s=n_s, sys_messages=sys_messages,
                           n_sy=n_sy
                           )

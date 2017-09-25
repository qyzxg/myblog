#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
import datetime
from ..models import User, Post, Comment, Todo, Message, UserInfo
from . import profile
from .. import db
from ..admin.views import get_c_month, get_m_days, get_day
from .forms import UserInfoForm
from ..shares import UploadToQiniu, allowed_file
import json
import os


# 用户资料页
@profile.route('/user/<username>/', methods=['GET'])
@login_required
def user_index(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('不存在用户：' + username + '！')
        return redirect(url_for('public.index'))
    if user.id != current_user.id:
        flash('您没有权限访问该页面!')
        return redirect(url_for('public.index'))
    user_ = UserInfo.query.get(user.id)
    n = get_c_month()
    days = get_m_days()
    lst = [
        Post.query.filter_by(author_id=user.id).filter(
            Post.created.between('2017-%s-%d 0:0:0' % (n, i), '2017-%s-%d 0:0:0' % (n, (i + 1)))).count()
        for i in range(1, days)]
    x = list(range(1, days))
    m = get_c_month()
    day = get_day()
    return render_template('profile/user_index.html', user=user, user_=user_,
                           title='%s的后台' % user.username,
                           menu=0, x=x, lst=lst, m=m, day=day, days=days)


# 修改用户资料
@profile.route('/modify_info/', methods=['POST', 'GET'])
@login_required
def modify_info():
    file = open(os.path.join(os.path.dirname(__file__), 'select.json'), 'r', encoding='utf-8')
    form = UserInfoForm()
    choices = json.load(file)
    form.gender.choices = choices['gender']
    form.graduated.choices = choices['graduated']
    form.position.choices = choices['position']
    form.industry.choices = choices['industry']
    form.education.choices = choices['education']
    form.language.choices = choices['language']
    file.close()
    user_ = UserInfo.query.get(current_user.id)
    if user_:
        form.age.data = user_.age
        form.gender.data = user_.gender
        form.education.data = user_.education
        form.graduated.data = user_.graduated
        form.position.data = user_.position
        form.company.data = user_.company
        form.industry.data = user_.industry
        form.language.data = user_.language
        form.website.data = user_.website
    if request.method == 'POST':
        if request.form:
            form1 = request.form
            age = form1['age'],
            gender = form1['gender'],
            education = form1['education'],
            graduated = form1['graduated'],
            position = form1['position'],
            company = form1['company'],
            industry = form1['industry'],
            language = form1['language'],
            website = form1['website'],
            user_info = UserInfo(
                age=age[0],
                gender=str(gender[0]),
                education=education[0],
                graduated=graduated[0],
                position=position[0],
                company=company[0],
                industry=industry[0],
                language=language[0],
                website=website[0],
                id=current_user.id,
            )
            if user_:
                user_.age = age[0] if age else user_.age
                user_.gender = gender[0] if gender else user_.gender
                user_.education = education[0] if education else user_.education
                user_.graduated = graduated[0] if graduated else user_.graduated
                user_.position = position[0] if position else user_.position
                user_.company = company[0] if company else user_.company
                user_.industry = industry[0] if industry else industry
                user_.language = language[0] if language else user_.language
                user_.website = website[0] if website else user_.website
            else:
                db.session.add(user_info)
                db.session.commit()
            flash('资料修改成功')
            return redirect(url_for('profile.user_index', username=current_user.username))
        if request.files['file']:
            file = request.files['file']
            if file and allowed_file(file.filename):
                domian_name = 'https://static.51qinqing.com'
                u = UploadToQiniu(file, 'avatar/')
                ret, info = u.upload()
                key = ret['key']
                current_user.avatar = domian_name + '/' + key
                return jsonify({"success": True})
            flash('文件格式不允许!')
    return render_template('profile/modify_info.html', title='修改资料', form=form)


@profile.route('/upload_zfbimg/', methods=['POST', 'GET'])
@login_required
def upload_zfbimg():
    if request.method == 'POST':
        if request.form:
            form = request.form
            if form['num']:
                current_user.zfb_num = form['num']
            flash('支付宝信息修改成功')
            return redirect(url_for('profile.user_reward_manage'))
        if request.files['file']:
            file = request.files['file']
            if allowed_file(file.filename):
                domian_name = 'https://static.51qinqing.com'
                u = UploadToQiniu(file, 'pay/zfb/')
                ret, info = u.upload()
                key = ret['key']
                current_user.zfb_img = domian_name + '/' + key
                return jsonify({"success": True})
            else:
                flash('文件格式不允许')
                return redirect(url_for('profile.upload_zfbimg'))
    return render_template('profile/upload_zfbimg.html', title='修改支付宝打赏信息')


@profile.route('/upload_wximg/', methods=['POST', 'GET'])
@login_required
def upload_wximg():
    if request.method == 'POST':
        if request.form:
            form = request.form
            if form['num']:
                current_user.wx_num = form['num']
            flash('微信信息修改成功')
            return redirect(url_for('profile.user_reward_manage'))
        if request.files['file']:
            file = request.files['file']
            if allowed_file(file.filename):
                domian_name = 'https://static.51qinqing.com'
                u = UploadToQiniu(file, 'pay/wx/')
                ret, info = u.upload()
                key = ret['key']
                current_user.wx_img = domian_name + '/' + key
                return jsonify({"success": True})
            else:
                flash('文件格式不允许')
                return redirect(url_for('profile.upload_wximg'))
    return render_template('profile/upload_wximg.html', title='修改微信打赏信息')


@profile.route('/others/<username>/', methods=['GET'])
def others(username):
    posts_ = Post.query.filter(Post.is_public == 1).order_by(Post.comment_times.desc()).limit(5)
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('不存在用户：' + username + '！')
        return redirect(url_for('public.index'))
    else:
        posts = Post.query.filter(Post.is_public == 1).filter_by(author_id=user.id)

    return render_template('profile/others.html', user=user, posts=posts,
                           title='%s的资料' % user.username,
                           posts_=posts_,
                           menu=0)


@profile.route('/user/blogs_manage/', methods=['GET'])
@login_required
def user_blogs_manage():
    posts = Post.query.filter_by(author_id=current_user.id)
    return render_template('profile/blogs_manage.html',
                           posts=posts,
                           title='博客管理',
                           menu=1)


@profile.route('/user/bolg_manage/<int:id_>/', methods=['POST', 'GET'])
@login_required
def user_blog_manage(id_):
    post = Post.query.filter_by(id=id_).first()
    user = User.query.filter_by(id=post.author_id).first()
    if post is None:
        flash('文章不存在!')
    if not current_user.is_authenticated:
        flash('请登录后再操作!')
    post.del_comments()
    post.del_tags()
    db.session.delete(post)
    db.session.commit()
    user.post_total -= 1
    flash('文章删除成功!')
    return redirect(url_for('profile.user_blogs_manage'))


@profile.route('/user/public_manage/<int:id_>/<int:public>/', methods=['POST', 'GET'])
@login_required
def user_public_manage(id_, public):
    post = Post.query.filter_by(id=id_).first()
    if not post:
        flash('文章不存在')
    post.is_public = 1 if int(public) == 1 else 0
    return redirect(url_for('profile.user_blogs_manage'))


@profile.route('/user/comments_manage/', methods=['GET'])
@login_required
def user_comments_manage():
    comments = Comment.query.filter_by(author_id=current_user.id)
    return render_template('profile/comments_manage.html',
                           comments=comments,
                           title='评论管理',
                           menu=3)


@profile.route('/user/comment_manage/<int:id_>/', methods=['POST', 'GET'])
@login_required
def user_comment_manage(id_):
    comment = Comment.query.filter_by(id=id_).first()
    if comment is None:
        flash('评论不存在!')
    if not current_user.is_authenticated:
        flash('请登录后再操作!')
    comment.delete_all_reply()
    db.session.delete(comment)
    db.session.commit()
    flash('评论删除成功!')
    return redirect(url_for('profile.user_comments_manage'))


@profile.route('/user/collects_manage/', methods=['GET'])
@login_required
def user_collects_manage():
    user = current_user
    posts = user.collected_posts()
    return render_template('profile/collects_manage.html',
                           posts=posts,
                           title='收藏管理',
                           menu=2)


@profile.route('/user/followers_manage/', methods=['GET'])
@login_required
def user_followers_manage():
    user = current_user
    followeds = user.followed_users()  # 自己关注的
    followers = user.follower_users()  # 关注自己的
    friends = [i for i in followeds if i in followers]
    return render_template('profile/followers_manage.html',
                           followers=followers,
                           followeds=followeds,
                           friends=friends,
                           title='好友管理',
                           menu=5)


@profile.route('/user/reward_manage/', methods=['GET'])
@login_required
def user_reward_manage():
    user = current_user
    return render_template('profile/user_reward_manage.html',
                           user=user, title='打赏管理', meun=7)


@profile.route('/user/collect_manage/<int:id_>/', methods=['POST', 'GET'])
@login_required
def user_collect_manage(id_):
    post = Post.query.get_or_404(id_)
    current_user.uncollect(post)
    flash('取消收藏成功!')
    return redirect(url_for('profile.user_collects_manage'))


@profile.route('/user/follow_manage/<username>/', methods=['POST', 'GET'])
@login_required
def user_follower_manage(username):
    user = User.query.filter_by(username=username).first()
    current_user.unfollow(user)
    flash('取消关注成功!')
    return redirect(url_for('profile.user_followers_manage'))


@profile.route('/user/todos_manage/', methods=['GET'])
@login_required
def user_todos_manage():
    todos = Todo.query.filter_by(user_id=current_user.id).order_by(Todo.created.desc())
    return render_template('profile/todos_manage.html', todos=todos,
                           title='TODO管理', menu=4)


@profile.route('/user/todo_add/', methods=['POST', 'GET'])
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


@profile.route('/user/todo_add/<int:id_>/', methods=['POST', 'GET'])
@login_required
def todo_done(id_):
    todo = Todo.query.get_or_404(id_)
    todo.status = 1
    todo.finished = datetime.datetime.now()
    db.session.add(todo)
    db.session.commit()
    flash('状态修改成功!')
    return redirect(url_for('profile.user_todos_manage'))


@profile.route('/user/todo_undone/<int:id_>/', methods=['POST', 'GET'])
@login_required
def todo_undone(id_):
    todo = Todo.query.get_or_404(id_)
    todo.status = 0
    todo.finished = None
    db.session.add(todo)
    db.session.commit()
    flash('状态修改成功!')
    return redirect(url_for('profile.user_todos_manage'))


@profile.route('/user/todo_dele/<int:id_>/', methods=['POST', 'GET'])
@login_required
def todo_dele(id_):
    todo = Todo.query.get_or_404(id_)
    db.session.delete(todo)
    db.session.commit()
    flash('todo删除成功!')
    return redirect(url_for('profile.user_todos_manage'))


# 收藏

@profile.route('/collect/<int:id_>/', methods=['POST', 'GET'])
@login_required
def collect(id_):
    post = Post.query.get_or_404(id_)
    if current_user.is_authenticated:
        if current_user.collecting(post):
            flash('你已经收藏了这篇文章!')
            return redirect(url_for('public.details', id_=post.id))
    else:
        flash('登录后才能收藏哦!')
        return redirect(url_for('public.details', id_=post.id))

    current_user.collect(post)
    flash('收藏成功!')
    return redirect(url_for('public.details', id_=post.id))


# 取消收藏

@profile.route('/uncollect/<int:id_>/', methods=['POST', 'GET'])
@login_required
def uncollect(id_):
    post = Post.query.get_or_404(id_)
    if not current_user.collecting(post):
        flash('你没有收藏这篇文章!')
        return redirect(url_for('public.details', id=post.id))
    current_user.uncollect(post)
    flash('取消收藏成功!')
    return redirect(url_for('public.details', id=post.id))


# 关注

@profile.route('/follow/<username>/', methods=['POST', 'GET'])
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


@profile.route('/unfollow/<username>/', methods=['POST', 'GET'])
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
                          sendto=user,
                          created_at=datetime.datetime.now())
        db.session.add(message)
        db.session.commit()
        flash('消息发送成功!')
    return redirect(url_for('profile.messages_manage'))


@profile.route('/delete_message/<int:id_>/', methods=['POST', 'GET'])
@login_required
def delete_message(id_):
    message = Message.query.filter_by(id=id_).first()
    if not message.confirmed:
        flash('对方还没有读过这条消息,不能删除!')
        return redirect(url_for('profile.messages_manage'))
    db.session.delete(message)
    db.session.commit()
    flash('消息删除成功!')
    return redirect(url_for('profile.messages_manage'))


@profile.route('/confirm_message/<int:id_>/', methods=['POST', 'GET'])
@login_required
def confirm_message(id_):
    message = Message.query.filter_by(id=id_).first()
    message.confirmed = 1
    flash('消息状态更改成功!')
    return redirect(url_for('profile.messages_manage'))


@profile.route('/messages_manage/', methods=['GET'])
@login_required
def messages_manage():
    user = current_user
    managers = User.query.filter_by(role=1).all()
    followeds = user.followed_users()  # 自己关注的
    followers = user.follower_users()  # 关注自己的
    friends1 = [i for i in followeds if i in followers]
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
    return render_template('profile/messages_manage.html', menu=6, title='消息管理', friends=friends,
                           unconfirmed_messages=unconfirmed_messages,
                           confirmed_messages=confirmed_messages,
                           sended_messages=sended_messages,
                           n_u=n_u, n_c=n_c, n_s=n_s, sys_messages=sys_messages,
                           n_sy=n_sy
                           )

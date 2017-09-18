#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_required, fresh_login_required
from sqlalchemy import func
import time
import datetime
from .. import db, cache
from . import admin
from ..models import User, Post, Comment, Categories, Message, LogInfo
from ..shares import admin_required
from .forms import NewCategory
import itertools
import psutil
from ..tasks.celery_tasks import send_email


@cache.memoize(timeout=300, unless=None)  # 获取每天文章总数,5分钟获取1次
def get_m_post():
    n = get_c_month()
    b = get_m_days()
    lst = [
        Post.query.filter(Post.created.between('2017-%s-%d 0:0:0' % (n, i), '2017-%s-%d 0:0:0' % (n, (i + 1)))).count()
        for
        i in range(1, b)]
    return lst


@cache.memoize(timeout=3600, unless=None)  # 获取文章分类,1小时1次
def get_a_cate():
    lst = [str(a.name) for a in Categories.query.all()]
    return lst


@cache.memoize(timeout=3600, unless=None)  # 获取每类文章数量,1小时1次
def get_a_cates():
    lst = [Post.query.filter_by(category=i).count() for i in get_a_cate()]
    return lst


@cache.memoize(timeout=300, unless=None)  # 获取每天用户注册数,5分钟获取一次
def get_m_user():
    n = get_c_month()
    b = get_m_days()
    lst = [User.query.filter(
        User.created_at.between('2017-%s-%d 0:0:0' % (n, i), '2017-%s-%d 0:0:0' % (n, (i + 1)))).count() for
           i in range(1, b)]
    return lst


@cache.memoize(timeout=600, unless=None)  # 获取每天pv数,10分钟获取一次
def get_m_pv():
    n = get_c_month()
    b = get_m_days()
    lst = [LogInfo.query.filter(
        LogInfo.time_r.between('2017-%s-%d 0:0:0' % (n, i), '2017-%s-%d 0:0:0' % (n, (i + 1)))).count() for
           i in range(1, b)]
    return lst


@cache.memoize(timeout=600, unless=None)  # 获取每天uv数,10分钟获取一次
def get_m_uv():
    n = get_c_month()
    b = get_m_days()
    lst = [len(set(LogInfo.query.with_entities(LogInfo.ip).filter(
        LogInfo.time_r.between('2017-%s-%d 0:0:0' % (n, i), '2017-%s-%d 0:0:0' % (n, (i + 1)))))) for
        i in range(1, b)]
    return lst


@cache.memoize(timeout=86400, unless=None)  # 获取当前月份,1天一次
def get_c_month():
    return time.strftime('%m', time.localtime(time.time()))


@cache.memoize(timeout=86400, unless=None)  # 获取当前日,1天一次
def get_day():
    return time.strftime('%d', time.localtime(time.time()))


@cache.memoize(timeout=86400, unless=None)  # 获取当前月天数,1天一次
def get_m_days():
    n = get_c_month()
    if n in ['01', '03', '05', '07', '08', '10', '12']:
        a = 32
    else:
        a = 31
    return a


@admin.route('/admin/get_server_info', methods=['GET', 'POST'])
def get_server_info():
    cpu = psutil.cpu_percent(interval=1)
    memory = float(psutil.virtual_memory().used) / float(psutil.virtual_memory().total) * 100.0
    last_disk = psutil.disk_io_counters(perdisk=False).read_bytes + psutil.disk_io_counters(perdisk=False).write_bytes
    last_network = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().packets_recv
    time.sleep(1)
    disk = (psutil.disk_io_counters(perdisk=False).read_bytes + psutil.disk_io_counters(
        perdisk=False).write_bytes - last_disk) / 1024
    network = (psutil.net_io_counters().bytes_sent + psutil.net_io_counters().packets_recv - last_network) / 1024

    server_info = {'code': 'Success', 'message': 'Success', 'cpu': int(cpu), 'memory': int(memory), 'disk': int(disk),
                   'network': int(network)}
    if not current_user.is_authenticated:
        return jsonify({'code': 'error', 'message': 'You must login!'})
    if current_user.role != 1:
        return jsonify({'code': 'error', 'message': 'Permission denied!'})
    return jsonify(server_info)


@admin.route('/admin/get_user_city', methods=['GET', 'POST'])
@fresh_login_required
@admin_required
def get_user_city():
    reg = db.session.query(User.city, func.count(User.city)).group_by(User.city).all()
    city = list(map(lambda lst: {'name': lst[0], 'value': lst[1]}, reg))
    return jsonify(city)


# 管理员后台首页

@admin.route('/admin', methods=['GET'])
# @fresh_login_required
@login_required
@admin_required
def admin_index():
    m = get_c_month()
    cat = get_a_cate()
    cats = get_a_cates()
    day = int(get_day())
    pv = get_m_pv()
    uv = get_m_uv()
    days = get_m_days()
    c = {k: v for k, v in itertools.zip_longest(cat, cats)}
    d = [{'value': v, 'name': k} for k, v in c.items()]
    x = list(range(1, days))
    lt_post = get_m_post()
    lt_user = get_m_user()
    return render_template('admin/admin_index.html', title='管理员后台',
                           menu=0,
                           x=x, lt_post=lt_post,
                           lt_user=lt_user,
                           m=m, cat=cat, cats=cats, d=d,
                           pv=pv, uv=uv, day=day, days=days,
                           )


# 文章分类管理
@admin.route('/admin/new_category/', methods=['POST', 'GET'])
@login_required
@admin_required
def new_category():
    categories = Categories.query.order_by(Categories.id)
    form = NewCategory()
    if form.validate_on_submit():
        category = Categories(
            name=form.name.data.strip(),
            name1=form.name.data.strip()
        )
        db.session.add(category)
        db.session.commit()
    return render_template('admin/new_category.html',
                           categories=categories,
                           form=form, menu=4, title='分类管理')


# 用户管理
@admin.route('/admin/users_manage/', methods=['GET'])
@login_required
@admin_required
def users_manage():
    users = User.query.order_by(User.post_total.desc())
    return render_template('admin/users_manage.html',
                           users=users,
                           title='用户管理', menu=1)


# 博客管理
@admin.route('/admin/blogs_manage', methods=['GET'])
@login_required
@admin_required
def blogs_manage():
    posts = Post.query.order_by(Post.read_times.desc())
    return render_template('admin/blogs_manage.html',
                           posts=posts,
                           title='博客管理',
                           menu=2)


@admin.route('/admin/blogs_delete', methods=['POST', 'GET'])
@login_required
@admin_required
def blogs_delete():
    if request.method == 'POST':
        try:
            id_str = request.form.get('id')
            id_lst = id_str.split("#")[:-1]
            for i in id_lst:
                post = Post.query.filter_by(id=str(i)).first()
                if not post:
                    pass
                else:
                    post.del_comments()
                    post.del_tags()
                    db.session.delete(post)
                    db.session.commit()
            flash('%d篇文章删除成功!' % len(id_lst))
            return "OK"
        except:
            return "ERROR"


@admin.route('/admin/users_delete', methods=['POST', 'GET'])
@login_required
@admin_required
def users_delete():
    if request.method == 'POST':
        try:
            id_str = request.form.get('id')
            id_lst = id_str.split("#")[:-1]
            for i in id_lst:
                user = User.query.filter_by(id=str(i)).first()
                if not user:
                    pass
                else:
                    user.del_comments()
                    user.del_todos()
                    user.delete_r_message()
                    user.delete_s_message()
                    posts = Post.query.filter_by(author_id=user.id).all()
                    for post in posts:
                        post.del_comments()
                        post.del_tags()
                        db.session.delete(post)
                    db.session.delete(user)
                    db.session.commit()
            flash('%d个用户删除成功!' % len(id_lst))
            return "OK"
        except:
            return "ERROR"


@admin.route('/admin/comments_delete', methods=['POST', 'GET'])
@login_required
@admin_required
def comments_delete():
    if request.method == 'POST':
        try:
            id_str = request.form.get('id')
            id_lst = id_str.split("#")[:-1]
            for i in id_lst:
                comment = Comment.query.filter_by(id=str(i)).first()
                if not comment:
                    pass
                else:
                    comment.delete_all_reply()
                    db.session.delete(comment)
                    db.session.commit()
            flash('%d条评论删除成功!' % len(id_lst))
            return "OK"
        except:
            return "ERROR"


# 评论管理
@admin.route('/admin/comments_manage', methods=['POST', 'GET'])
@login_required
@admin_required
def comments_manage():
    comments = Comment.query.order_by(Comment.created.desc())
    return render_template('admin/comments_manage.html',
                           comments=comments,
                           title='评论管理',
                           menu=3)


# 博客删除
@admin.route('/admin/bolg_manage/<int:id>/', methods=['POST', 'GET'])
@login_required
@admin_required
def blog_manage(id):
    post = Post.query.filter_by(id=id).first()
    user = User.query.filter_by(id=post.author_id).first()
    user.post_total -= 1
    if post is None:
        flash('文章不存在!')
    post.del_comments()
    post.del_tags()
    db.session.delete(post)
    db.session.commit()
    user.post_total -= 1
    flash('文章删除成功!')
    return redirect(url_for('admin.blogs_manage'))


# 评论删除
@admin.route('/admin/comment_manage/<int:id>/', methods=['POST', 'GET'])
@login_required
@admin_required
def comment_manage(id):
    comment = Comment.query.filter_by(id=id).first()
    if comment is None:
        flash('评论不存在!')
    comment.delete_all_reply()
    db.session.delete(comment)
    db.session.commit()
    flash('评论删除成功!')
    return redirect(url_for('admin.comments_manage'))


# 用户登录管理
@admin.route('/admin/login_manage/<int:id>/<int:status>/<int:delete>/', methods=['POST', 'GET'])
@login_required
@admin_required
def login_manage(id, status, delete):
    user = User.query.filter_by(id=id).first()
    if user is None:
        flash('用户不存在!')
    else:
        posts = Post.query.filter_by(author_id=user.id).all()
        if int(status) == 1:
            user.status = 1
        else:
            user.status = 0
        if int(delete) == 1:
            # 同时删除该用户的文章和评论
            user.del_comments()
            user.delete_r_message()
            user.delete_s_message()
            for post in posts:
                post.del_comments()
                post.del_tags()
                db.session.delete(post)
            db.session.delete(user)
            db.session.commit()
            flash('用户删除成功!')
    return redirect(url_for('admin.users_manage'))


# 角色管理
@admin.route('/admin/role_manage/<int:id>/<int:role>/', methods=['POST', 'GET'])
@login_required
@admin_required
def role_manage(id, role):
    user = User.query.filter_by(id=id).first()
    if user is None:
        flash('用户不存在!')
    else:
        if int(role) == 1:
            user.role = 1
        else:
            user.role = 0
    return redirect(url_for('admin.users_manage'))


@admin.route('/admin/messages_manage/', methods=['GET'])
@login_required
@admin_required
def messages_manage():
    users = User.query.all()
    sended_messages = Message.query.order_by(Message.created_at.desc()).filter_by(sender=current_user)
    return render_template('admin/messages_manage.html', sended_messages=sended_messages, users=users,
                           title='通知管理', menu=5)


@admin.route('/admin/send_messages/', methods=['POST', 'GET'])
@login_required
@admin_required
def send_messages():
    users = User.query.all()
    form = request.form
    cates = form['cate']
    content = form['content']
    if cates == '系统全体':
        for user in users:
            message = Message(content=content,
                              sender=current_user,
                              sendto=user,
                              created_at=datetime.datetime.now())
            db.session.add(message)
        db.session.commit()
        flash('全体通知发送成功')
    elif cates == '邮件全体':
        for user in users:
            subject = u"[noreply][51datas]通知邮件"
            html = render_template('admin/email_notice.html', user=user, content=content)
            send_email.delay(user.email, subject, html)
            message = Message(content=content,
                              sender=current_user,
                              sendto=user,
                              created_at=datetime.datetime.now(),
                              cate=2)
            db.session.add(message)
        db.session.commit()
        flash('发送全体邮件/通知成功')
    else:
        user = User.query.filter_by(username=cates).first()
        subject = u"[noreply][51datas]通知邮件"
        html = render_template('admin/email_notice.html', user=user, content=content)
        send_email.delay(user.email, subject, html)
        message = Message(content=content,
                          sender=current_user,
                          sendto=user,
                          created_at=datetime.datetime.now(),
                          cate=2)
        db.session.add(message)
        db.session.commit()
        flash('发送邮件/通知成功')
    return redirect(url_for('admin.messages_manage'))


@admin.route('/admin/delete_messages/<int:id>/', methods=['POST', 'GET'])
@login_required
@admin_required
def delete_message(id):
    message = Message.query.filter_by(id=id).first()
    if not message.confirmed:
        flash('对方还没有读过这条消息,不能删除!')
        return redirect(url_for('admin.messages_manage'))
    db.session.delete(message)
    db.session.commit()
    flash('通知删除成功')
    return redirect(url_for('admin.messages_manage'))

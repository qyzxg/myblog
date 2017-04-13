#!/usr/bin/python
# -*- coding:utf-8 -*-


from . import auth
from flask import render_template, flash, redirect, url_for, request
from .. import db

from .forms import LoginForm, RegistForm, AuthEmail, ResetPassword
from flask_login import current_user, login_user, login_required, logout_user
import datetime
from ..token import generate_confirmation_token, confirm_token
from ..email import send_email
from ..models import User



# 用户注册
@auth.route('/register', methods=['POST', 'GET'])
def register():
    form = RegistForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            username=form.username.data,
            password=form.password.data,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
            last_login=datetime.datetime.now(),
            confirmed=False
        )

        user.set_password(form.data['password'])
        db.session.add(user)
        db.session.commit()
        token = generate_confirmation_token(user.email)
        confirm_url = url_for('auth.confirm_email', token=token, _external=True)
        html = render_template('auth/email.html', confirm_url=confirm_url)
        subject = "Please confirm your email"
        send_email(user.email, subject, html)
        login_user(user, remember=True)
        flash('注册成功,请登录您的邮箱按照提示激活账户')
        return redirect(url_for('public.index'))
    return render_template('auth/register.html', form=form, title='用户注册')

# 注册邮件确认
@auth.route('/confirm/<token>')
@login_required
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('确认链接不可用或已过期!', 'danger')
    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('您的账户已经激活过了!', 'success')
    else:
        user.confirmed = True
        user.confirmed_on = datetime.datetime.now()
        db.session.add(user)
        db.session.commit()
        flash('您的账户已激活,谢谢!', 'success')
    return redirect(url_for('public.index'))


# 发送激活邮件
@auth.route('/active', methods=['POST', 'GET'])
@login_required
def active():
    user = current_user
    token = generate_confirmation_token(user.email)
    confirm_url = url_for('auth.confirm_email', token=token, _external=True)
    html = render_template('auth/email.html', confirm_url=confirm_url)
    subject = "Please confirm your email"
    send_email(user.email, subject, html)
    flash('激活邮件已发送至您的邮箱!')
    return redirect(url_for('profile.user_index', username=user.username))


# 用户登录
@auth.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        user = form.get_user()
        if user is None:
            flash('用户不存在')
            return redirect(url_for('auth.login'))
        if not user.check_password(data['password']):
            flash('密码错误')
            return redirect(url_for('auth.login'))
        if user.status == 0:
            flash('您的账户已经被限制登录')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        user.last_login = datetime.datetime.now()
        flash('欢迎回来,%s' % current_user.username)
        next_url = request.args.get('next')
        return redirect(next_url or url_for('public.index'))
    return render_template('auth/login.html', form=form, title='用户登录')


# 用户登出
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('public.index'))

# 重置密码邮箱确认
@auth.route('/reset/confirm_email', methods=["GET", "POST"])
def reset_confirm_email():
    form = AuthEmail()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash('该邮箱还没有注册!')
            return redirect(url_for('auth.reset_confirm_email'))
        else:
            subject = "Password reset confirm email"
            token = generate_confirmation_token(user.email)
            confirm_url = url_for('auth.reset_password', token=token, _external=True)
            html = render_template('auth/email.html', confirm_url=confirm_url)
            send_email(user.email, subject, html)
            flash('验证邮件已发送至您的邮箱!')
            return redirect(url_for('public.index'))
    return render_template('auth/auth_email.html', form=form, title='邮箱验证')


# 重置密码
@auth.route('/reset/reset_password/<token>', methods=["GET", "POST"])
def reset_password(token):
    try:
        email = confirm_token(token)
    except:
        flash('链接已过期!')
    form = ResetPassword()
    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first()
        user.password = form.password.data
        user.set_password(form.data['password'])
        db.session.add(user)
        db.session.commit()
        logout_user()
        flash('密码修改成功,请重新登录!')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form, token=token,
                           title='重置密码')



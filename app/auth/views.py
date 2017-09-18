#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask import render_template, flash, redirect, url_for, request, \
    session, send_file, make_response, json, jsonify
from flask_login import current_user, login_user, login_required, logout_user
import datetime
import requests
from . import auth
from .. import db, qq
from .forms import LoginForm, RegistForm, AuthEmail, ResetPassword
from ..token import generate_confirmation_token, confirm_token
from ..tasks.celery_tasks import send_email
from ..models import User
from .g_validate import generate_verify_image
import io
from app import redis_store


# 获取验证码
@auth.route('/get_validate/', methods=['GET'])
def get_validate():
    image, text = generate_verify_image()
    byte_io = io.BytesIO()
    image.save(byte_io, 'jpeg')
    img_data = byte_io.getvalue()
    byte_io.close()
    response = make_response(img_data)
    # byte_io.seek(0)
    response.headers['Content-Type'] = 'image/jpg'
    session['code_text'] = text
    # return send_file(byte_io, mimetype='image/png')
    return response


# 用户注册
@auth.route('/register/', methods=['POST', 'GET'])
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
        html = render_template('auth/email_register.html', confirm_url=confirm_url)
        subject = u"[noreply][51qinqing-python之家]账号注册邮件"
        # send_email(user.email, subject, html)
        send_email.delay(user.email, subject, html)  # 异步
        user = db.session.merge(user)
        login_user(user, remember=True)
        flash('注册成功,请登录您的邮箱按照提示激活账户')
        return redirect(url_for('public.index'))
    return render_template('auth/register.html', form=form, title='用户注册')


# 邮件确认
@auth.route('/confirm/<token>/', methods=['POST', 'GET'])
@login_required
def confirm_email(token):
    try:
        email = confirm_token(token)
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
    except:
        flash('确认链接不可用或已过期!', 'danger')


# 发送激活邮件
@auth.route('/active/', methods=['POST', 'GET'])
@login_required
def active():
    user = current_user
    token = generate_confirmation_token(user.email)
    confirm_url = url_for('auth.confirm_email', token=token, _external=True)
    html = render_template('auth/email_active.html', confirm_url=confirm_url)
    subject = u"[noreply][51qinqing-python之家]账号激活邮件"
    # send_email(user.email, subject, html)  # send_email.delay() 异步
    send_email.delay(user.email, subject, html)  # 异步
    flash('激活邮件已发送至您的邮箱!')
    return redirect(url_for('profile.user_index', username=user.username))


# 用户登录
@auth.route('/login/', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        form_data = form.data
        user = form.get_user()
        if user is None:
            flash('用户不存在')
            return redirect(url_for('auth.login'))
        if user.status == 0:
            flash('该账户已经被限制登录')
            return redirect(url_for('auth.login'))
        if not user.check_password(form_data['password']):
            flash('密码错误,请重试!')
            return redirect(url_for('auth.login'))
        if 'code_text' in session and form_data['validate'].lower() != session['code_text'].lower():
            flash(u'验证码错误！')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        user.last_login = datetime.datetime.now()
        redis_store.delete('validateCount:%d' % user.id)
        try:
            ip_addr = request.headers['X-real-ip']
        except:
            ip_addr = request.remote_addr
        url = requests.get('http://ip.taobao.com/service/getIpInfo.php?ip=%s' % ip_addr)
        data = url.json()
        user.ip_addr = ip_addr
        user.country = data['data']['country']
        user.area = data['data']['area']
        user.region = data['data']['region']
        user.city = data['data']['city']
        user.county = data['data']['county']
        flash('欢迎回来,%s' % user.username)
        next_url = request.args.get('next')
        return redirect(next_url or url_for('public.index'))
    return render_template('auth/login.html', title='用户登录', form=form)


# 用户登出
@auth.route('/logout/', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    flash('您已成功登出,期待再次光临.')
    return redirect(url_for('public.index'))


# 重置密码邮箱确认
@auth.route('/reset/confirm_email/', methods=["GET", "POST"])
def reset_confirm_email():
    form = AuthEmail()
    if form.validate_on_submit():
        uemail = form.email.data
        user = User.query.filter_by(email=uemail).first()
        if not user:
            flash('该邮箱还没有注册!')
            return redirect(url_for('auth.reset_confirm_email'))
        else:
            subject = u"[noreply][51qinqing-python之家]重置密码邮件"
            token = generate_confirmation_token(user.email)
            confirm_url = url_for('auth.reset_password', token=token, _external=True)
            html = render_template('auth/email_reset.html', confirm_url=confirm_url)
            # send_email(user.email, subject, html)  # send_email.delay() 异步
            send_email.delay(user.email, subject, html)  # 异步
            flash('验证邮件已发送至您的邮箱!')
            return redirect(url_for('public.index'))
    return render_template('auth/auth_email.html', form=form, title='邮箱验证')


# 重置密码
@auth.route('/reset/reset_password/<token>/', methods=["GET", "POST"])
def reset_password(token):
    try:
        email = confirm_token(token)
        form = ResetPassword()
        if form.validate_on_submit():
            user = User.query.filter_by(email=email).first()
            user.password = form.password.data
            user.set_password(form.data['password'])
            user.updated_at = datetime.datetime.now()
            db.session.add(user)
            db.session.commit()
            logout_user()
            flash('密码修改成功,请重新登录!')
            return redirect(url_for('auth.login'))
    except:
        flash('链接已过期!')
    return render_template('auth/reset_password.html', form=form, token=token,
                           title='重置密码')


# 第三方登录
@auth.route('/qq/login/')
def qq_login():
    return qq.authorize(callback=url_for('auth.qq_authorized', _external=True))


def json_to_dict(x):
    '''OAuthResponse class can't not parse the JSON data with content-type
    text/html, so we need reload the JSON data manually'''
    if x.find('callback') > -1:
        pos_lb = x.find('{')
        pos_rb = x.find('}')
        x = x[pos_lb:pos_rb + 1]
    try:
        return json.loads(x, encoding='utf-8')
    except:
        return x


@auth.route('/qq/authorized')
def qq_authorized():
    resp = qq.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['qq_token'] = (resp['access_token'], '')
    resp = qq.get('/oauth2.0/me', {'access_token': session['qq_token'][0]})
    resp = json_to_dict(resp.data.decode('utf-8'))
    if isinstance(resp, dict):
        session['qq_openid'] = resp.get('openid')
    return redirect(url_for('auth.get_qq_user_info'))


def update_qq_api_request_data():
    '''Update some required parameters for OAuth2.0 API calls'''
    defaults = {
        'openid': session.get('qq_openid'),
        'access_token': session.get('qq_token')[0],
        'oauth_consumer_key': '',
    }
    return defaults


@auth.route('/qq/user_info/')
def get_qq_user_info():
    if 'qq_token' in session:
        data = update_qq_api_request_data()
        resp = qq.get('/user/get_user_info', data=data)
        user_info = json_to_dict(resp.data.decode('utf-8'))
        user_info.update({'status': resp.status})
        open_id = session['qq_openid']
        user = User.query.filter_by(open_id=str(open_id)).first()
        if user:
            login_user(user)
            return redirect(url_for('public.index'))
        else:
            new_user = User(
                email='{}@qq.com'.format(open_id[-10:]),
                username=user_info['nickname'],
                password=open_id,
                created_at=datetime.datetime.now(),
                updated_at=datetime.datetime.now(),
                last_login=datetime.datetime.now(),
                confirmed=True,
                region=user_info['province'],
                city=user_info['city'],
                avatar=user_info['figureurl_qq_2'],
                open_id=open_id,
                confirmed_on=datetime.datetime.now(),
                binded=0
            )
            new_user.set_password(str(open_id))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('public.index'))
    return redirect(url_for('auth.login'))


@qq.tokengetter
def get_qq_oauth_token():
    return session.get('qq_token')

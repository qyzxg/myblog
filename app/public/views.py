#!/usr/bin/python
# -*- coding:utf-8 -*-

from flask import render_template, make_response, flash, redirect, \
    url_for, request, send_from_directory, g, current_app, json
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import flask_whooshalchemyplus as whoosh
from os import path
import time
import datetime
import random
from ..tasks.celery_tasks import get_post_img
from .. import db, cache
from . import public
from ..models import User, Post, Comment, Categories, Styles, Todo, Tag
from .forms import PostForm, CommentForm, SearchForm
import os
from werkzeug.contrib.atom import AtomFeed
from urllib.parse import urljoin
from qiniu import Auth, put_file, put_data


# 搜索
@public.before_app_request
def before_request():
    from .. import create_app
    app = create_app()
    whoosh.whoosh_index(app, Post)
    g.search_form = SearchForm()


# 定义过滤器
def wdcount(stri):
    return len(stri)


public.add_app_template_filter(wdcount, name='wdcount')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']


class UploadToQiniu():
    def __init__(self, domian_name, bucket_name, file, expire=3600):
        self.access_key = 'iDfXDpVa4pxFW4tyqkJK8dPkeSeRPlEsGZN7qnST'
        self.secret_key = 'iT3Z4r_z23zauKlyAsTCj51t6WOtJWbADhPKn2O6'
        self.bucket_name = bucket_name
        self.domian_name = domian_name
        self.file = file
        self.expire = expire

    def upload(self):
        user = current_user
        ext = self.file.filename.split('.')[-1]
        time_ = str(time.time()).replace('.', '')
        k = time_ + '_' + str(user.id) + '.' + ext
        q = Auth(self.access_key, self.secret_key)
        token = q.upload_token(self.bucket_name, k, self.expire)
        return put_data(token, k, self.file.read())


@cache.cached(timeout=30, key_prefix='view_%s', unless=None)
@public.route('/', methods=['POST', 'GET'])
def index():
    # 记录cookie
    page_index = request.args.get('page', 1, type=int)
    query = Post.query.filter(Post.is_public == 1).order_by(Post.read_times.desc())
    pagination = query.paginate(page_index, per_page=10, error_out=False)
    posts_ = Post.query.filter(Post.is_public == 1).order_by(Post.comment_times.desc()).limit(5)
    hot_authors = User.query.order_by(User.post_total.desc()).limit(5)
    todos = None
    if current_user.is_authenticated:
        todos = Todo.query.filter_by(user_id=current_user.id, status=0)
    posts = pagination.items
    categories = Categories.query.all()
    tags = Tag.query.all()
    response = make_response(render_template('public/index.html',
                                             title='PyData',
                                             posts_=posts_,
                                             posts=posts,
                                             pagination=pagination,
                                             todos=todos,
                                             hot_authors=hot_authors,
                                             categories=categories,
                                             tags=tags))
    response.set_cookie(key='user', value='name', expires=time.time() + 3600)
    response.set_cookie(key='pass', value='word', expires=time.time() + 3600)
    return response


# 上传图像
@public.route('/upload_avatar/', methods=['POST', 'GET'])
@login_required
def upload_avatar():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            domian_name = 'http://oqqu0qp5g.bkt.clouddn.com'
            bucket_name = 'avatar'
            u = UploadToQiniu(domian_name, bucket_name, file)
            ret, info = u.upload()
            key = ret['key']
            current_user.avatar = domian_name + '/' + key
            flash('图像修改成功!')
            return redirect(url_for('public.upload_avatar'))
        flash('您上传的文件不合法!')
    return render_template('public/upload_avatar.html', title='上传图像')


@public.route('/upload_zfbimg/', methods=['POST', 'GET'])
@login_required
def upload_zfbimg():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            form = request.form
            domian_name = 'http://oqquasfn4.bkt.clouddn.com'
            bucket_name = 'zfbimg'
            u = UploadToQiniu(domian_name, bucket_name, file)
            ret, info = u.upload()
            key = ret['key']
            current_user.zfb_img = domian_name + '/' + key
            current_user.zfb_num = form['num']
            flash('支付宝二维码上传成功!')
            return redirect(url_for('public.upload_zfbimg'))
        flash('您上传的文件不合法!')
    return render_template('public/upload_zfbimg.html', title='上传支付宝二维码')


@public.route('/upload_wximg/', methods=['POST', 'GET'])
@login_required
def upload_wximg():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            form = request.form
            domian_name = 'http://oqqur6lkr.bkt.clouddn.com'
            bucket_name = 'wximg'
            u = UploadToQiniu(domian_name, bucket_name, file)
            ret, info = u.upload()
            key = ret['key']
            current_user.wx_img = domian_name + '/' + key
            current_user.wx_num = form['num']
            flash('微信二维码上传成功!')
            return redirect(url_for('public.upload_wximg'))
        flash('您上传的文件不合法!')
    return render_template('public/upload_wximg.html', title='上传微信二维码')


# 文章图片上传
@public.route('/edit/upload_postimg/', methods=['POST', 'GET'])
@login_required
def upload_postimg():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            domian_name = 'http://oqquiobc2.bkt.clouddn.com'
            bucket_name = 'postimg'
            u = UploadToQiniu(domian_name, bucket_name, file)
            ret, info = u.upload()
            key = ret['key']
            return '{"error":false,"path":"' + domian_name + '/' + key + '"}'
        else:
            flash('您上传的文件不合法')
            return redirect(url_for('public.edit'))


# 发表/修改文章
@public.route('/edit/', methods=['POST', 'GET'])
@public.route('/edit/<int:id>/', methods=['POST', 'GET'])
@login_required
def edit(id=0):
    form = PostForm()
    s = [('--请选择文章来源--', '--请选择文章来源--')]
    form.style.choices = s + [(str(a.name1), str(a.name)) for a in Styles.query.all()]
    c = [('--请选择文章分类--', '--请选择文章分类--')]
    form.category.choices = c + [(str(a.name1), str(a.name)) for a in Categories.query.all()]
    if id == 0:
        post = Post(author_id=current_user.id)
    else:
        post = Post.query.get_or_404(id)
    user = User.query.filter_by(id=current_user.id).first()
    if Post.query.filter(Post.is_public == 1).filter_by(author_id=current_user.id):
        user.post_total = len(Post.query.filter(Post.is_public == 1).filter_by(author_id=current_user.id).all())
    if user.confirmed == 1:
        if form.validate_on_submit():
            post.body = form.body.data
            post.title = form.title.data.strip()
            post.style = form.style.data
            post.category = form.category.data
            post.is_public = form.is_public.data

            alltags = [i.name for i in Tag.query.all()]
            ptags = [i.name for i in post.tags]
            l = form.tags.data.split(',')
            ls = filter(None, l)
            for i in ls:
                if i == '':
                    l.remove(i)
                if i.strip() not in alltags:
                    tag = Tag(name=i.strip())
                    db.session.add(tag)
                    post.tags.append(tag)
                else:
                    if i.strip() in ptags:
                        pass
                    else:
                        post.tags.append(Tag.query.filter_by(name=i.strip()).first())
            if post.style == '--请选择文章来源--' or post.category == '--请选择文章分类--':
                flash('请选择文章来源和分类')
                return redirect(url_for('public.edit'))
            db.session.add(post)
            db.session.commit()
            post.post_img = post.get_post_img(post)

            # 异步获取
            # img = get_post_img.delay(post)
            # post.post_img = img.get()

            user.post_total += 1
            flash('文章发表成功!')
            return redirect(url_for('public.details', id=post.id))
    else:
        flash('要发表文章请先验证您的邮箱')
        return redirect(url_for('public.index'))
    form.title.data = post.title
    form.body.data = post.body
    form.style.data = post.style
    form.category.data = post.category
    # if not post.is_public:
    #     form.is_public.render_kw = ''
    # else:
    #     form.is_public.render_kw = {'checked':'checked'}
    posttags = []
    s = ''
    if post.tags:
        for i in post.tags:
            posttags.append(i.name)
        s = ','.join(posttags)
    form.tags.data = s
    title = '添加新文章'
    if id > 0:
        title = '编辑文章'

    return render_template('public/edit_post.html',
                           title=title,
                           form=form,
                           post=post)


# 文章详情页
@public.route('/post/details/<int:id>', methods=['POST', 'GET'])
def details(id):
    post = Post.query.get_or_404(id)
    post.comment_times = len(post.comments)
    posts_ = Post.query.filter(Post.is_public == 1).order_by(Post.comment_times.desc()).limit(5)
    hot_authors = User.query.order_by(User.post_total.desc()).limit(5)
    post.read_times += 1
    categories = Categories.query.all()
    form = CommentForm()
    todos = None
    if current_user.is_authenticated:
        todos = Todo.query.filter_by(user_id=current_user.id, status=0)
    if request.method == 'POST':
        if current_user.is_authenticated:
            if current_user.confirmed == 1:
                comment = Comment(author=current_user,
                                      body=request.form['body'],
                                      post=post)
                db.session.add(comment)
                db.session.commit()
                post.comment_times += 1
                form.body.data = ''
                result = {"status": "success"}
                return json.dumps(result)
            else:
                flash('验证邮箱后才能发表评论哦!')

        else:
            flash('登录后才能评论哦!')
    pre_p = Post.query.filter(Post.id < id).order_by(Post.id.desc()).limit(1).all()
    next_p = Post.query.filter(Post.id > id).order_by(Post.id).limit(1).all()
    if pre_p:
        pre_post=pre_p[0]
    else:
        pre_post=None
    if next_p:
        next_post = next_p[0]
    else:
        next_post=None

    page_index = request.args.get('page', 1, type=int)
    query = Comment.query.filter_by(post_id=id).order_by(Comment.created.desc())
    pagination = query.paginate(page_index, per_page=10, error_out=False)
    comments = pagination.items
    return render_template('public/details.html',
                           title=post.title,
                           form=form,
                           post=post,
                           posts_=posts_,
                           todos=todos,
                           pagination=pagination,
                           comments=comments,
                           categories=categories,
                           hot_authors=hot_authors,
                           pre_post=pre_post, next_post=next_post
                           )


@public.route('/get_comments', methods=['POST', 'GET'])
def get_comments():
    if request.method == "POST":
        try:
            post_id = request.form.get('post_id')
        except:
            pass
        comments = Comment.query.filter_by(post_id=int(post_id)).order_by(Comment.created.desc())
        return render_template('includes/_comments_list.html', comments=comments)


@public.route('/hot_posts/')
def hot_posts():
    return render_template('includes/_hot_posts.html')


# 搜索
@public.before_app_request
def before_request():
    from .. import create_app
    app = create_app()
    whoosh.whoosh_index(app, Post)
    g.search_form = SearchForm()


@public.route('/search/', methods=['POST', 'GET'])
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('public.index'))
    return redirect(url_for('public.search_results', key_word=g.search_form.search.data))


@public.route('/search_results/<key_word>/', methods=['POST', 'GET'])
def search_results(key_word):
    page_index = request.args.get('page', 1, type=int)

    query = Post.query.whoosh_search(key_word, current_app.config['MAX_SEARCH_RESULTS']).filter(Post.is_public == 1)
    pagination = query.paginate(page_index, per_page=10, error_out=False)
    results = pagination.items
    total = len(query.all())
    return render_template('public/search_results.html',
                           key_word=key_word,
                           results=results,
                           total=total,
                           pagination=pagination,
                           title='%s的搜索结果' % key_word)


@public.route('/service/')
def service():
    posts_ = Post.query.filter(Post.is_public == 1).order_by(Post.comment_times.desc()).limit(5)
    return render_template('public/service.html', title='服务', posts_=posts_)


@public.route('/about/')
def about():
    posts_ = Post.query.filter(Post.is_public == 1).order_by(Post.comment_times.desc()).limit(5)
    return render_template('public/about.html', title='关于', posts_=posts_)


def make_external(url):
    return urljoin(request.url_root, url)


@public.route('/rss/')
def recent_feed():
    feed = AtomFeed('最近文章',
                    feed_url=request.url, url=request.url_root)
    posts = Post.query.filter(Post.is_public == 1).order_by(Post.created.desc()) \
        .limit(20).all()
    for post in posts:
        feed.add(post.title, post.body,
                 content_type='html',
                 author=post.author.username,
                 id=post.id,
                 updated=post.created,
                 url=make_external(url_for('public.details', id=post.id))
                 )
    return feed.get_response()

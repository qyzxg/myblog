#!/usr/bin/python
# -*- coding:utf-8 -*-

from flask import render_template, make_response, flash, redirect, \
    url_for, request, send_from_directory, g, current_app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import flask_whooshalchemyplus as whoosh
from os import path
import time
from ..tasks.celery_tasks import get_post_img
from .. import db
from . import public
from ..models import User, Post, Comment, Categories, Styles, Todo
from .forms import PostForm, CommentForm, SearchForm



@public.route('/', methods=['POST', 'GET'])
def index():
    # 记录cookie
    page_index = request.args.get('page', 1, type=int)

    query = Post.query.order_by(Post.read_times.desc())

    pagination = query.paginate(page_index, per_page=10, error_out=False)
    posts_ = Post.query.order_by(Post.comment_times.desc()).limit(5)
    todos = None
    if current_user.is_authenticated:
        todos = Todo.query.filter_by(user_id=current_user.id, status=0)
    posts = pagination.items
    response = make_response(render_template('public/index.html',
                                             title='博客首页',
                                             posts_=posts_,
                                             posts=posts,
                                             pagination=pagination,
                                             todos=todos))
    response.set_cookie(key='user', value='name', expires=time.time() + 3600)
    response.set_cookie(key='pass', value='word', expires=time.time() + 3600)
    return response



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']


# 文件上传
@public.route('/upload/', methods=['POST', 'GET'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            basepath = current_app.config['BASE_PATH']
            uploadpath = path.join(basepath, current_app.config['UPLOAD_FOLDER'])
            file.save(uploadpath + '_' + str(current_user.id) + '_' + filename)
            current_user.avatar = r'/static/avatar/avatar' + '_' + str(current_user.id) + '_' + filename
            flash('图像修改成功!')
            return redirect('upload')
        flash('您上传的文件不合法!')
    return render_template('public/upload.html', title='上传图像')


@public.route('/uploaded_file/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


# 发表/修改文章
@public.route('/edit/', methods=['POST', 'GET'])
@public.route('/edit/<int:id>', methods=['POST', 'GET'])
@login_required
def edit(id=0):
    form = PostForm()
    form.style.choices = [(str(a.name1), str(a.name)) for a in Styles.query.all()]
    form.category.choices = [(str(a.name1), str(a.name)) for a in Categories.query.all()]
    if id == 0:
        post = Post(author_id=current_user.id)
    else:
        post = Post.query.get_or_404(id)
    user = User.query.filter_by(id=current_user.id).first()
    if Post.query.filter_by(author_id=current_user.id):
        user.post_total = len(Post.query.filter_by(author_id=current_user.id).all())
    if user.confirmed == 1:
        if form.validate_on_submit():
            post.body = form.body.data
            post.title = form.title.data
            post.style = form.style.data
            post.category = form.category.data
            img = get_post_img.delay(post)
            post.post_img = img.get()
            db.session.add(post)
            db.session.commit()
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
    posts_ = Post.query.order_by(Post.comment_times.desc()).limit(5)
    post.read_times += 1

    form = CommentForm()
    # if not current_user.is_authenticated :
    todos = None
    if current_user.is_authenticated:
        todos = Todo.query.filter_by(user_id=current_user.id, status=0)
    if form.validate_on_submit():

        if current_user.is_authenticated:
            if current_user.confirmed == 1:
                comment = Comment(author=current_user,
                                  body=form.body.data,
                                  post=post)
                db.session.add(comment)
                db.session.commit()
                post.comment_times += 1
                flash('评论发表成功!')
            else:
                flash('验证邮箱后才能发表评论哦!')

        else:
            flash('登录后才能评论哦!')
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
                           comments=comments
                           )


@public.route('/hot_posts/')
def hot_posts():
    # posts = Post.query.order_by(Post.read_times.desc()).limit(3)
    return render_template('includes/_hot_posts.html')


# 搜索
@public.before_app_request
def before_request():
    from .. import create_app
    app = create_app()
    whoosh.whoosh_index(app, Post)
    g.search_form = SearchForm()



@public.route('/search', methods=['POST', 'GET'])
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('public.index'))
    return redirect(url_for('public.search_results', query=g.search_form.search.data))


@public.route('/search_results/<query>', methods=['POST', 'GET'])
def search_results(query):
    results = Post.query.whoosh_search(query, current_app.config['MAX_SEARCH_RESULTS']).all()
    return render_template('public/search_results.html',
                           query=query,
                           results=results,
                           title='%s的搜索结果' % query)


@public.route('/service')
def service():
    posts_ = Post.query.order_by(Post.comment_times.desc()).limit(5)
    return render_template('public/service.html', title='服务', posts_=posts_)


@public.route('/about')
def about():
    posts_ = Post.query.order_by(Post.comment_times.desc()).limit(5)
    return render_template('public/about.html', title='关于', posts_=posts_)




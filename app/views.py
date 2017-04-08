from app import app, db
from flask import render_template, make_response, flash, redirect, \
    url_for, request, send_from_directory, g
from app.models import User, Post, Comment, Categories, Styles,Todo
from app.forms import LoginForm, RegistForm, PostForm, CommentForm, NewCategory, SearchForm, \
    AuthEmail,ResetPassword
from flask_login import current_user, login_user, login_required, logout_user
import datetime
from app.token import generate_confirmation_token, confirm_token
from app.email import send_email
from werkzeug.utils import secure_filename
from os import path
import time

#首页
@app.route('/', methods=['POST', 'GET'])
def index():
    # 记录cookie

    page_index = request.args.get('page', 1, type=int)

    query = Post.query.order_by(Post.read_times.desc())

    pagination = query.paginate(page_index, per_page=10, error_out=False)
    posts_ = Post.query.order_by(Post.comment_times.desc()).limit(5)
    todos = None
    if current_user.is_authenticated:
        todos = Todo.query.filter_by(user_id=current_user.id,status=0)
    posts = pagination.items
    response = make_response(render_template('index.html',
                                             title='博客首页',
                                             posts_=posts_,
                                             posts=posts,
                                             pagination=pagination,
                                             todos = todos))
    response.set_cookie(key='user', value='name', expires=time.time() + 3600)
    response.set_cookie(key='pass', value='word', expires=time.time() + 3600)
    return response


@app.route('/service')
def service():

    posts_ = Post.query.order_by(Post.comment_times.desc()).limit(5)
    return render_template('service.html', title='服务',posts_=posts_)


@app.route('/about')
def about():
    posts_ = Post.query.order_by(Post.comment_times.desc()).limit(5)
    return render_template('about.html', title='关于',posts_=posts_)

#用户注册
@app.route('/register', methods=['POST', 'GET'])
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
        confirm_url = url_for('confirm_email', token=token, _external=True)
        html = render_template('email.html', confirm_url=confirm_url)
        subject = "Please confirm your email"
        send_email(user.email, subject, html)
        login_user(user, remember=True)
        flash('注册成功,请登录您的邮箱按照提示激活账户')
        return redirect(url_for('index'))
    return render_template('register.html', form=form, title='用户注册')

#注册邮件确认
@app.route('/confirm/<token>')
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
    return redirect(url_for('index'))

#发送激活邮件
@app.route('/active', methods=['POST', 'GET'])
@login_required
def active():
    user = current_user
    token = generate_confirmation_token(user.email)
    confirm_url = url_for('confirm_email', token=token, _external=True)
    html = render_template('email.html', confirm_url=confirm_url)
    subject = "Please confirm your email"
    send_email(user.email, subject, html)
    flash('激活邮件已发送至您的邮箱!')
    return redirect(url_for('user_index',username=user.username))

#用户登录
@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        user = form.get_user()
        if user is None:
            flash('用户不存在')
            return redirect(url_for('login'))
        if not user.check_password(data['password']):
            flash('密码错误')
            return redirect(url_for('login'))
        if user.status == 0:
            flash('您的账户已经被限制登录')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        user.last_login = datetime.datetime.now()
        flash('欢迎回来,%s' % current_user.username)
        next_url = request.args.get('next')
        return redirect(next_url or url_for('index'))
    return render_template('login.html', form=form, title = '用户登录')

#用户登出
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# 用户资料页
@app.route('/user/<username>', methods=['POST', 'GET'])
@login_required
def user_index(username):
    user = User.query.filter_by(username=username).first()
    if user == None:
        flash('不存在用户：' + username + '！')
        return redirect(url_for('index'))

    if user.id != current_user.id:
        flash('您没有权限访问该页面!')
        return redirect(url_for('index'))

    return render_template('user/user_index.html', user=user,
                           title='%s的后台' % user.username,
                           menu=0)

@app.route('/others/<username>', methods=['POST', 'GET'])
def others(username):
    page_index = request.args.get('page', 1, type=int)
    posts_ = Post.query.order_by(Post.comment_times.desc()).limit(5)
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('不存在用户：' + username + '！')
        return redirect(url_for('index'))
    else:
        query = Post.query.filter_by(author_id=user.id)
        pagination = query.paginate(page_index, per_page=10, error_out=False)
        posts = pagination.items

    return render_template('user/others.html', user=user,posts=posts,
                           title='%s的资料' % user.username,
                           pagination = pagination,posts_=posts_,
                           menu=0)

@app.route('/user/blogs_manage', methods=['POST', 'GET'])
@login_required
def user_blogs_manage():
    page_index = request.args.get('page', 1, type=int)

    query = Post.query.filter_by(author_id=current_user.id)

    pagination = query.paginate(page_index, per_page=10, error_out=False)

    posts = pagination.items

    return render_template('user/blogs_manage.html',
                               posts=posts,
                               pagination=pagination,
                               title='博客管理',
                               menu=1)


@app.route('/user/bolg_manage/<int:id>/')
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
    return redirect(url_for('user_blogs_manage'))

@app.route('/user/comments_manage', methods=['POST', 'GET'])
@login_required
def user_comments_manage():

    page_index = request.args.get('page', 1, type=int)

    query = Comment.query.filter_by(author_id=current_user.id)

    pagination = query.paginate(page_index, per_page=10, error_out=False)

    comments = pagination.items

    return render_template('user/comments_manage.html',
                               comments=comments,
                               pagination=pagination,
                               title='评论管理',
                               menu=3)


@app.route('/user/comment_manage/<int:id>/')
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
    return redirect(url_for('user_comments_manage'))


@app.route('/user/collects_manage', methods=['POST', 'GET'])
@login_required
def user_collects_manage():
    page_index = request.args.get('page', 1, type=int)
    user = current_user
    query = user.collected_posts()

    pagination = query.paginate(page_index, per_page=10, error_out=False)

    posts = pagination.items

    return render_template('user/collects_manage.html',
                               posts=posts,
                               pagination=pagination,
                               title='收藏管理',
                               menu=2)

@app.route('/user/collect_manage/<int:id>/')
@login_required
def user_collect_manage(id):
    post = Post.query.get_or_404(id)
    current_user.uncollect(post)
    flash('取消收藏成功!')
    return redirect(url_for('user_collects_manage'))

@app.route('/user/todos_manage', methods=['POST', 'GET'])
@login_required
def user_todos_manage():
    page_index = request.args.get('page', 1, type=int)
    query = Todo.query.filter_by(user_id=current_user.id).order_by(Todo.created.desc())
    pagination = query.paginate(page_index, per_page=10, error_out=False)
    todos = pagination.items
    return render_template('user/todos_manage.html', todos=todos,
                           title = 'TODO管理',menu=4,pagination=pagination,)

@app.route('/user/todo_add', methods=['POST','GET' ])
@login_required
def todo_add():
    form = request.form
    content = form['content']
    if not content:
        flash('todo内容不能为空!')
        return redirect(url_for('user_todos_manage'))
    else:
        todo = Todo(content=content,created=datetime.datetime.now(), user_id=current_user.id)
        db.session.add(todo)
        db.session.commit()
        flash('todo添加成功!')
    return redirect(url_for('user_todos_manage'))


@app.route('/user/todo_add/<int:id>')
@login_required
def todo_done(id):
    todo = Todo.query.get_or_404(id)
    todo.status = 1
    todo.finished = datetime.datetime.now()
    db.session.add(todo)
    db.session.commit()
    flash('状态修改成功!')
    return redirect(url_for('user_todos_manage'))

@app.route('/user/todo_undone/<int:id>')
@login_required
def todo_undone(id):
    todo = Todo.query.get_or_404(id)
    todo.status = 0
    todo.finished = None
    db.session.add(todo)
    db.session.commit()
    flash('状态修改成功!')
    return redirect(url_for('user_todos_manage'))

@app.route('/user/todo_dele/<int:id>')
@login_required
def todo_dele(id):
    todo = Todo.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    flash('todo删除成功!')
    return redirect(url_for('user_todos_manage'))

#重置密码邮箱确认
@app.route('/reset/confirm_email', methods=["GET", "POST"])
def reset_confirm_email():
    form = AuthEmail()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash('该邮箱还没有注册!')
            return redirect(url_for('reset_confirm_email'))
        else:
            subject = "Password reset confirm email"
            token = generate_confirmation_token(user.email)
            confirm_url = url_for('reset_password',token=token,_external=True)
            html = render_template('email.html', confirm_url=confirm_url)
            send_email(user.email, subject, html)
            flash('验证邮件已发送至您的邮箱!')
            return redirect(url_for('index'))
    return render_template('auth_email.html', form=form,title = '邮箱验证')

#重置密码
@app.route('/reset/reset_password/<token>', methods=["GET", "POST"])
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
        flash('密码修改成功!')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form, token=token,
                           title = '重置密码')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

#文件上传
@app.route('/upload/', methods=['POST', 'GET'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            basepath = app.config['BASE_PATH']
            uploadpath = path.join(basepath, app.config['UPLOAD_FOLDER'])
            file.save(uploadpath + '_' + str(current_user.id) + '_' + filename)
            current_user.avatar = r'/static/avatar/avatar' + '_' + str(current_user.id) + '_' + filename
            flash('图像修改成功!')
            return redirect('upload')
        flash('您上传的文件不合法!')
    return render_template('upload.html', title='上传图像')


@app.route('/uploaded_file/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

#文章详情页
@app.route('/post/details/<int:id>', methods=['POST', 'GET'])
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

    return render_template('details.html',
                           title=post.title,
                           form=form,
                           post=post,
                           posts_=posts_,
                           todos=todos,
                           )


#收藏
@login_required
@app.route('/collect/<int:id>')
def collect(id):
    post=Post.query.get_or_404(id)
    if current_user.is_authenticated:
        if current_user.collecting(post):
            flash('你已经收藏了这篇文章!')
            return redirect(url_for('details',id=post.id))
    else:
        flash('登录后才能收藏哦!')
        return redirect(url_for('details', id=post.id))

    current_user.collect(post)
    flash('收藏成功!')
    return redirect(url_for('details',id=post.id))

#取消收藏
@login_required
@app.route('/uncollect/<int:id>')
def uncollect(id):
    post = Post.query.get_or_404(id)
    if not current_user.collecting(post):
        flash('你没有收藏这篇文章!')
        return redirect(url_for('details', id=post.id))
    current_user.uncollect(post)
    flash('取消收藏成功!')
    return redirect(url_for('details', id=post.id))



# 发表/修改文章
@app.route('/edit/', methods=['POST', 'GET'])
@app.route('/edit/<int:id>', methods=['POST', 'GET'])
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
            post.post_img = post.get_post_img(post)
            db.session.add(post)
            db.session.commit()
            user.post_total += 1
            flash('文章发表成功!')
            return redirect(url_for('.details', id=post.id))
    else:
        flash('要发表文章请先验证您的邮箱')
        return redirect(url_for('.index'))
    form.title.data = post.title
    form.body.data = post.body
    form.style.data = post.style
    form.category.data = post.category

    title = '添加新文章'
    if id > 0:
        title = '编辑文章'

    return render_template('edit_post.html',
                           title=title,
                           form=form,
                           post=post)


@app.route('/hot_posts/')
def hot_posts():
    posts = Post.query.order_by(Post.read_times.desc()).limit(3)
    return render_template('includes/_hot_posts.html')

# 搜索
@app.before_request
def before_request():
    g.search_form = SearchForm()


@app.route('/search', methods=['POST', 'GET'])
# @login_required
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    return redirect(url_for('search_results', query=g.search_form.search.data))


@app.route('/search_results/<query>', methods=['POST', 'GET'])
# @login_required
def search_results(query):
    results = Post.query.whoosh_search(query, app.config['MAX_SEARCH_RESULTS']).all()
    return render_template('search_results.html',
                           query=query,
                           results=results,
                           title = '%s的搜索结果' % query)


'''后台管理部分'''

#管理员后台首页
@app.route('/admin')
@login_required
def admin_index():
    if current_user.role == 0:
        flash('您没有管理员权限!')
        return render_template('user/user_index.html', user=current_user,
                               title = '用户首页')

    else:
        return render_template('admin/admin_index.html', title='管理员后台',
                               menu=0)

#文章分类管理
@app.route('/admin/new_category', methods=['POST', 'GET'])
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
@app.route('/admin/users_manage', methods=['POST', 'GET'])
@login_required
def users_manage():
    page_index = request.args.get('page', 1, type=int)

    query = User.query.order_by(User.post_total.desc())

    pagination = query.paginate(page_index, per_page=10, error_out=False)

    users = pagination.items
    if current_user.role == 0:
        flash('您没有管理员权限!')
        return redirect(url_for('index'))
    else:
        return render_template('admin/users_manage.html',
                               users=users,
                               pagination=pagination,
                               title='用户管理', menu=1)

#博客管理
@app.route('/admin/blogs_manage', methods=['POST', 'GET'])
@login_required
def blogs_manage():
    page_index = request.args.get('page', 1, type=int)

    query = Post.query.order_by(Post.read_times.desc())

    pagination = query.paginate(page_index, per_page=10, error_out=False)

    posts = pagination.items
    if current_user.role == 0:
        flash('您没有管理员权限!')
        return redirect(url_for('index'))
    else:
        return render_template('admin/blogs_manage.html',
                               posts=posts,
                               pagination=pagination,
                               title='博客管理',
                               menu=2)

# 评论管理
@app.route('/admin/comments_manage', methods=['POST', 'GET'])
@login_required
def comments_manage():
    page_index = request.args.get('page', 1, type=int)

    query = Comment.query.order_by(Comment.created.desc())

    pagination = query.paginate(page_index, per_page=10, error_out=False)

    comments = pagination.items
    if current_user.role == 0:
        flash('您没有管理员权限!')
        return redirect(url_for('index'))
    else:
        return render_template('admin/comments_manage.html',
                               comments=comments,
                               pagination=pagination,
                               title='评论管理',
                               menu=3)


# 博客删除
@app.route('/admin/bolg_manage/<int:id>/')
@login_required
def blog_manage(id):
    if current_user.role == 0:
        flash('您没有管理员权限!')
        return redirect(url_for('index'))
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
        return redirect(url_for('blogs_manage'))
        # flash('文章删除成功')


# 评论删除
@app.route('/admin/comment_manage/<int:id>/')
@login_required
def comment_manage(id):
    if current_user.role == 0:
        flash('您没有管理员权限!')
        return redirect(url_for('index'))
    else:
        comment = Comment.query.filter_by(id=id).first()
        if comment is None:
            flash('评论不存在!')
        if not current_user.is_authenticated:
            flash('请登录后再操作!')
        db.session.delete(comment)
        db.session.commit()
        flash('评论删除成功!')
        return redirect(url_for('comments_manage'))


# 用户登录管理
@app.route('/admin/login_manage/<int:id>/<int:status>/<int:delete>')
@login_required
def login_manage(id, status, delete):
    if current_user.role == 0:
        flash('您没有管理员权限!')
        return redirect(url_for('index'))
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
        return redirect(url_for('users_manage'))


# 角色管理
@app.route('/admin/role_manage/<int:id>/<int:role>/')
@login_required
# @admin_permission_requied
def role_manage(id, role):
    if current_user.role == 0:
        flash('您没有管理员权限!')
        return redirect(url_for('index'))
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
        return redirect(url_for('users_manage'))


@app.route('/user_id/<int:uid>')
def user_id(uid):
    return '您的id是:%d' % uid

    # 处理404页面


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html',title = '404'), 404

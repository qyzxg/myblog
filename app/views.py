from app import app, db
from flask import render_template, make_response, flash, redirect, url_for, request, send_from_directory
from app.models import User, Post, Comment
from app.forms import LoginForm, RegistForm, PostForm, CommentForm
from flask_login import current_user, login_user, login_required, logout_user
import datetime
from app.token import generate_confirmation_token, confirm_token
from app.email import send_email
from werkzeug.utils import secure_filename
from os import path
import time
from app.decoratiors import admin_permission_requied

@app.route('/', methods=['POST', 'GET'])
def index():
    # 记录cookie

    page_index = request.args.get('page', 1, type=int)

    query = Post.query.order_by(Post.read_times.desc())

    pagination = query.paginate(page_index, per_page=5, error_out=False)

    posts = pagination.items
    response = make_response(render_template('index.html',
                                             title='myblog',
                                             posts=posts,
                                             pagination=pagination))
    response.set_cookie(key='user', value='name', expires=time.time() + 3600)
    response.set_cookie(key='pass', value='word', expires=time.time() + 3600)
    return response


@app.route('/service')
def service():
    return render_template('service.html')


@app.route('/about')
def about():
    return render_template('about.html')


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
    return render_template('register.html', form=form)


@app.route('/confirm/<token>')
@login_required
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('确认链接不可用或已过期!', 'danger')
    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('您的账户已激活. 请登录!', 'success')
    else:
        user.confirmed = True
        user.confirmed_on = datetime.datetime.now()
        db.session.add(user)
        db.session.commit()
        flash('您的账户已激活,谢谢!', 'success')
    return redirect(url_for('index'))


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
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# 用户资料页
@app.route('/user/<username>', methods=['POST', 'GET'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    if user == None:
        flash('不存在用户：' + username + '！')
        return redirect(url_for('index'))
    return render_template('profile.html', user=user)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


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
            flash('图像修改成功')
            return redirect('upload')
        flash('您上传的文件不合法!')
    return render_template('upload.html')


@app.route('/uploaded_file/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/post/details/<int:id>', methods=['POST', 'GET'])
def details(id):
    post = Post.query.get_or_404(id)
    post.comment_times = len(post.comments)

    post.read_times += 1
    form = CommentForm()
    # if not current_user.is_authenticated :

    if form.validate_on_submit():

        if current_user.is_authenticated:
            if current_user.confirmed == 1:
                comment = Comment(author=current_user,
                              body=form.body.data,
                              post=post)
                db.session.add(comment)
                db.session.commit()
                post.comment_times += 1
                flash('评论发表成功')
            else:
                flash('验证邮箱后才能发表评论哦!')

        else:
            flash('登录后才能评论哦!')

    return render_template('details.html',
                           title=post.title,
                           form=form,
                           post=post,
                           )

#发表/修改文章
@app.route('/edit/', methods=['POST', 'GET'])
@app.route('/edit/<int:id>', methods=['POST', 'GET'])
@login_required
def edit(id=0):
    form = PostForm()

    if id == 0:
        post = Post(author_id=current_user.id)
    else:
        post = Post.query.get_or_404(id)
    user = User.query.filter_by(id=current_user.id).first()
    if Post.query.filter_by(author_id=current_user.id):
        user.post_total = len(Post.query.filter_by(author_id=current_user.id).all())
    if user.confirmed==1:
        if form.validate_on_submit():
            post.body = form.body.data
            post.title = form.title.data
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

    title = '添加新文章'
    if id > 0:
        title = '编辑文章'

    return render_template('edit_post.html',
                           title=title,
                           form=form,
                           post=post)

@app.route('/ckupload/', methods=['POST'])
def ckupload():
    """file/img upload interface"""
    form = PostForm()
    response = form.upload(name=app)
    return response



'''后台管理部分'''


@app.route('/admin')
@login_required

def admin_index():
    if current_user.role==0:
        flash('您没有管理员权限!')
        return render_template('profile.html', user=current_user)

    else:
        return render_template('admin/admin_index.html',title = '后台首页',
                           menu=0)


@app.route('/admin/users_manage', methods=['POST', 'GET'])
@login_required

def users_manage():
    page_index = request.args.get('page', 1, type=int)

    query = User.query.order_by(User.post_total.desc())

    pagination = query.paginate(page_index, per_page=5, error_out=False)

    users = pagination.items
    if current_user.role==0:
        flash('您没有管理员权限!')
        return redirect(url_for('index'))
    else:
        return render_template('admin/users_manage.html',
                           users=users,
                           pagination=pagination,
                           title='用户管理',menu=1)


@app.route('/admin/blogs_manage', methods=['POST', 'GET'])
@login_required

def blogs_manage():
    page_index = request.args.get('page', 1, type=int)

    query = Post.query.order_by(Post.read_times.desc())

    pagination = query.paginate(page_index, per_page=10, error_out=False)

    posts = pagination.items
    if current_user.role==0:
        flash('您没有管理员权限!')
        return redirect(url_for('index'))
    else:
        return render_template('admin/blogs_manage.html',
                           posts=posts,
                           pagination=pagination,
                           title='博客管理',
                           menu=2)


@app.route('/admin/comments_manage', methods=['POST', 'GET'])
@login_required

def comments_manage():
    page_index = request.args.get('page', 1, type=int)

    query = Comment.query.order_by(Comment.created.desc())

    pagination = query.paginate(page_index, per_page=10, error_out=False)

    comments = pagination.items
    if current_user.role==0:
        flash('您没有管理员权限!')
        return redirect(url_for('index'))
    else:
        return render_template('admin/comments_manage.html',
                           comments=comments,
                           pagination=pagination,
                           title='评论管理',
                           menu=3)


# 博客管理
@app.route('/admin/bolg_manage/<int:id>/')
@login_required

def blog_manage(id):
    if current_user.role==0:
        flash('您没有管理员权限!')
        return redirect(url_for('index'))
    else:
        post = Post.query.filter_by(id=id).first()
        comments = Comment.query.filter_by(post_id=post.id).all()
        if post is None:
            flash('文章不存在!')
        if not current_user.is_authenticated:
            flash('请登录后再操作!')
        for i in comments:
            db.session.delete(i)
        db.session.delete(post)
        db.session.commit()
        flash('文章删除成功!')
        return redirect(url_for('blogs_manage'))
    # flash('文章删除成功')

# 评论管理
@app.route('/admin/comment_manage/<int:id>/')
@login_required

def comment_manage(id):
    if current_user.role==0:
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
    # flash('评论删除成功')

# 用户登录管理
@app.route('/admin/login_manage/<int:id>/<int:status>/<int:delete>')
@login_required

def login_manage(id, status, delete):
    if current_user.role==0:
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

#角色管理
@app.route('/admin/role_manage/<int:id>/<int:role>/')
@login_required
# @admin_permission_requied
def role_manage(id,role):
    if current_user.role==0:
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

# @app.route('/admin/role_manage', methods=['POST', 'GET'])
# @login_required
# def role_manage():
#     pass


@app.route('/user_id/<int:uid>')
def user_id(uid):
    return '您的id是:%d' % uid

    # 处理404页面


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

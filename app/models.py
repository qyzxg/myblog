from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import datetime


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False, doc='用户名')
    password = db.Column(db.String(200), unique=False, nullable=False, doc='密码')
    email = db.Column(db.String(200), unique=True, nullable=False, doc='邮箱')
    avatar = db.Column(db.String(200), doc='个人头像地址', default=r'/static/avatar/default_avatar.png')
    status = db.Column(db.Integer, default=1, doc='用户的状态')
    is_valid = db.Column(db.Boolean, default=True)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime, doc='最后登录时间')
    posts = db.relationship('Post', backref='author')
    comments = db.relationship('Comment', backref='author')
    post_total = db.Column(db.Integer, default=0)
    role = db.Column(db.Integer, default=0)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_status(self):

        if self.status == 1:
            return '正常'
        else:
            return '受限'

    def get_roles(self):

        if self.role == 1:
            return '管理'
        else:
            return '用户'

    def __repr__(self):
        return '<User %r>' % self.username


@login_manager.user_loader
def load_user(user_id):
    """ 登录回调"""
    return User.query.get(user_id)


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.Text)
    created = db.Column(db.DateTime, index=True, default=datetime.datetime.now())
    comment_times = db.Column(db.Integer, default=0)
    read_times = db.Column(db.Integer, default=0)
    comments = db.relationship('Comment', backref='post')
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    style = db.Column(db.String(50), default='原创')
    category = db.Column(db.String(50), default='Python')


class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    name1 = db.Column(db.String(50))


class Styles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    name1 = db.Column(db.String(50))


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(1000))
    created = db.Column(db.DateTime, index=True, default=datetime.datetime.now())
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

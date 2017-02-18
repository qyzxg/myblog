from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from markdown import markdown
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
    # role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    posts = db.relationship('Post', backref='author')
    comments = db.relationship('Comment', backref='author')
    post_total = db.Column(db.Integer, default=0)
    role = db.Column(db.Integer,default=0)
    # def __init__(self, username, password, email, created_at, updated_at,last_login):
    #     self.email = email
    #     self.username = username
    #     self.set_password(password)
    #     self.created_at = created_at
    #     self.updated_at = updated_at
    #     self.last_login = last_login

    # @staticmethod
    # def on_created(target, value, oldvalue, initiator):
    #     target.role = Role.query.filter_by(name='Guests').first()

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_status(self):

        if self.status ==1:
            return '正常'
        else:
            return '受限'
    def get_roles(self):

        if self.role ==1:
            return '管理'
        else:
            return '用户'

    def __repr__(self):
        return '<User %r>' % self.username

# db.event.listen(User.username, 'set', User.on_created)

@login_manager.user_loader
def load_user(user_id):
    """ 登录回调"""
    return User.query.get(user_id)



# class Role(db.Model):
#     __tablename__ = 'roles'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(20))
#     users = db.relationship('User', backref='role')
#
#     @staticmethod
#     def seed():
#         db.session.add_all(map(lambda r: Role(name=r), ['Guest', 'Admin']))
#         db.session.commit()

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.String(10000))
    body_html = db.Column(db.String(10000))
    created = db.Column(db.DateTime, index=True, default=datetime.datetime.now())
    comment_times = db.Column(db.Integer,default=0)
    read_times = db.Column(db.Integer,default=0)
    comments = db.relationship('Comment', backref='post')
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    style = db.Column(db.String(30),default='原创')
    category = db.Column(db.String(30), default='Python')

    @staticmethod
    def on_body_changed(target, value, oldvalue, initiator):
        if value is None or (value is ''):
            target.body_html = ''
        else:
            target.body_html = markdown(value)


db.event.listen(Post.body, 'set', Post.on_body_changed)

# class PostStyles(db.Model):
#     __tablename__ = 'poststyles'
#     id = id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(20))
#     post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
#     def __init__(self,name):
#         self.name = name
    # def get_poststyles(self):
    #     if self.name==1:
    #         return '原创'
    #     else:
    #         return '转载'

# class PostCategories(db.Model):
#     __tablename__ = 'postcategories'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(30))
#     post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
#
#     def __init__(self, name):
#         self.name = name

class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    name1 = db.Column(db.String(30))

class Styles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    name1 = db.Column(db.String(30))

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(300))
    created = db.Column(db.DateTime, index=True, default=datetime.datetime.now())
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import datetime
from jieba.analyse import ChineseAnalyzer
import re
from . import db, login_manager

follow = db.Table('followers',
                  db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
                  db.Column('followed_id', db.Integer, db.ForeignKey('users.id'))
                  )

collect = db.Table('collects',
                   db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                   db.Column('post_id', db.Integer, db.ForeignKey('posts.id'))
                   )


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
    collects = db.relationship('Post', secondary=collect, backref=db.backref('collected', lazy='dynamic'),
                               lazy='dynamic')
    todos = db.relationship('Todo', backref='user')
    followed = db.relationship('User',
                               secondary=follow,
                               primaryjoin=id == follow.c.follower_id,
                               secondaryjoin=id == follow.c.followed_id,
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')

    messages_reve = db.relationship('Message', backref='sender', lazy='dynamic',
                                    primaryjoin='Message.sender_id==User.id')
    messages_send = db.relationship('Message', backref='sendto', lazy='dynamic',
                                    primaryjoin='Message.sendto_id==User.id')

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

    # 收藏/取消收藏

    def collect(self, post):
        if not self.collecting(post):
            self.collects.append(post)
            return self

    def uncollect(self, post):
        if self.collecting(post):
            self.collects.remove(post)

    def collecting(self, post):
        if self.collects.filter(collect.c.post_id == post.id).count() > 0:
            return True
        else:
            return False

    def collected_posts(self):
        return Post.query.join(collect, (collect.c.post_id == Post.id)).filter(
            collect.c.user_id == self.id).order_by(Post.created.desc())

    # 关注/取消关注
    def follow(self, user):
        if not self.following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.following(user):
            self.followed.remove(user)
            return self

    def following(self, user):
        return self.followed.filter(follow.c.followed_id == user.id).count() > 0

    def followed_users(self):
        return User.query.join(follow, (follow.c.followed_id == User.id)).filter(
            follow.c.follower_id == self.id).order_by(User.post_total.desc())

    def __repr__(self):
        return '<User %r>' % self.username

    def unconfirmed_messages(self):
        unconfirmed_messages = Message.query.order_by(Message.created_at.desc()).filter_by(
            sendto=self).filter_by(
            confirmed=False).all()
        return len(unconfirmed_messages)


@login_manager.user_loader
def load_user(user_id):
    """ 登录回调"""
    return User.query.get(user_id)


class Post(db.Model):
    __tablename__ = 'posts'
    __searchable__ = ['title', 'body']
    __analyzer__ = ChineseAnalyzer()
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
    post_img = db.Column(db.String(500), doc='文章首页地址', default=r'/static/images/post_default.jpg')

    def get_post_img(self, post):
        reg = r'<img alt.*?src="(.*?)".*?/>'
        img = re.compile(reg)
        img_list = img.findall(post.body)
        if img_list:
            self.post_img = ''.join(img_list[0])
        return self.post_img

    def to_json(self):
        json = {
            # 'url': url_for('api.get_post', id=self.id, _external=True),
            'body': self.body,
            'created': self.created,
            # 'author': url_for('api.get_user', id=self.author_id,
            #                   _external=True),
            # 'comments': url_for('api.get_post_comments', id=self.id,
            #                     _external=True),
            'comment_count': self.comment_times
        }
        return json


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


class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(100))
    created = db.Column(db.DateTime, index=True, default=datetime.datetime.now())
    finished = db.Column(db.DateTime)
    status = db.Column(db.Integer, default=0, doc='完成状态')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def get_status(self):
        if self.status == 0:
            return '未完成'
        else:
            return '已完成'


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    confirmed = db.Column(db.Boolean, default=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    sendto_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<Message %r  from %r sent to %r>' % (self.content, self.sender.username, self.sendto.username)

    def get_status(self):
        if self.confirmed:
            return '已读'
        else:
            return '未读'

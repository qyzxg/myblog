from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import datetime
from jieba.analyse import ChineseAnalyzer
import re
from . import db, login_manager
from flask import current_app, request, url_for
import time

follow = db.Table('followers',
                  db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
                  db.Column('followed_id', db.Integer, db.ForeignKey('users.id'))
                  )

collect = db.Table('collects',
                   db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                   db.Column('post_id', db.Integer, db.ForeignKey('posts.id'))
                   )

tag = db.Table('tag',
               db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')),
               db.Column('post_id', db.Integer, db.ForeignKey('posts.id'))
               )


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))

    def __init__(self, name):
        self.name = name

    def get_total(self):
        tag_ = Tag.query.filter_by(name=self.name).first()
        posts = tag_.posts.filter(Post.is_public==1)
        total = len(posts.all())
        return total


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False, doc='用户名')
    password = db.Column(db.String(200), unique=False, nullable=False, doc='密码')
    email = db.Column(db.String(200), unique=True, nullable=False, doc='邮箱')
    avatar = db.Column(db.String(200), doc='个人头像地址', default=r'http://oqqu0qp5g.bkt.clouddn.com/default_avatar.jpg')
    status = db.Column(db.Integer, default=1, doc='用户的状态')
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True,index=True,)
    created_at = db.Column(db.DateTime,index=True)
    updated_at = db.Column(db.DateTime,index=True)
    ip_addr = db.Column(db.String(50), doc='IP地址')
    country = db.Column(db.String(30), doc='国家')
    area = db.Column(db.String(30), doc='地区')
    region = db.Column(db.String(30), doc='省份')
    city = db.Column(db.String(30), doc='城市')
    county = db.Column(db.String(30), doc='区县')
    last_login = db.Column(db.DateTime, doc='最后登录时间', index=True)
    posts = db.relationship('Post', backref='author')
    comments = db.relationship('Comment', backref='author')
    post_total = db.Column(db.Integer, default=0)
    role = db.Column(db.Integer, default=0)
    zfb_img = db.Column(db.String(200), doc='支付宝二维码', default=r'http://oqquasfn4.bkt.clouddn.com/default_zfb.png')
    wx_img = db.Column(db.String(200), doc='微信二维码', default=r'http://oqqur6lkr.bkt.clouddn.com/default_wx.png')
    zfb_num = db.Column(db.String(20), doc='支付宝金额', default='1.99')
    wx_num = db.Column(db.String(20), doc='微信金额', default='1.99')
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

    def to_json(self):
        json_user = {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'username': self.username,
            'last_login': self.last_login,
            'posts': url_for('api.get_user_posts', id=self.id, _external=True),
            'collected_posts': url_for('api.get_user_collected_posts',
                                       id=self.id, _external=True),
            'post_total': self.post_total
        }
        return json_user

    def del_comments(self):
        comments = Comment.query.filter_by(author_id=self.id).all()
        if comments:
            for comment in comments:
                db.session.delete(comment)
                db.session.commit()

    def del_todos(self):
        todos = Todo.query.filter_by(user_id=self.id).all()
        if todos:
            for todo in todos:
                db.session.delete(todo)
                db.session.commit()


    def __repr__(self):
        return '<User %r>' % self.username


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
    is_public = db.Column(db.Boolean, default=True)
    post_img = db.Column(db.String(500), doc='文章首页地址', default=r'http://oqquiobc2.bkt.clouddn.com/default_post_img.jpg')
    tags = db.relationship('Tag', secondary=tag,
                           backref=db.backref('posts', lazy='dynamic'))
    def get_public(self):
        if self.is_public:
            return '公开'
        else:
            return '隐藏'

    def get_post_img(self, post):
        reg = r'<img src="(.*?)".*?/>'
        img = re.compile(reg)
        img_list = img.findall(post.body)
        if img_list:
            self.post_img = ''.join(img_list[0])
        return self.post_img

    def to_json(self):
        json_post = {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'title': self.title,
            'body': self.body,
            'created': self.created,
            'author': url_for('api.get_user', id=self.author_id,
                              _external=True),
            'comments': url_for('api.get_post_comments', id=self.id,
                                _external=True),
            'comment_times': self.comment_times
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        title = json_post.get('title')
        return Post(body=body, title=title)

    def del_comments(self):
        comments = Comment.query.filter_by(post_id=self.id).all()
        if comments:
            for i in comments:
                db.session.delete(i)
                db.session.commit()

    def del_tags(self):
        tags = self.tags
        if tags:
            for i in tags:
                self.tags.remove(i)



class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    name1 = db.Column(db.String(50))

    def get_total(self):
        p = Post.query.filter(Post.is_public==1).filter_by(category=self.name).all()
        total = len(p)
        return total


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

    def to_json(self):
        json_comment = {
            'url': url_for('api.get_comment', id=self.id, _external=True),
            'post': url_for('api.get_post', id=self.post_id, _external=True),
            'body': self.body,
            'created': self.created,
            'author': url_for('api.get_user', id=self.author_id,
                              _external=True),
        }
        return json_comment

    @staticmethod
    def from_json(json_comment):
        body = json_comment.get('body')
        return Comment(body=body)

    def __repr__(self):
        return '<Comment %r,%r >' % (self.body, self.author)


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
    created_at = db.Column(db.DateTime, index=True, default=datetime.datetime.now())
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


# class SystemInfo(db.Model):
#     pass


class LogInfo(db.Model):
    __tablename__ = 'loginfo'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(50))
    time_r = db.Column(db.DateTime)
    status_code = db.Column(db.Integer)
    length = db.Column(db.Integer)
    url = db.Column(db.String(200))
    req_time = db.Column(db.Float)
    res_time = db.Column(db.Float)
    time_stamp = db.Column(db.Integer)

    def __repr__(self):
        return 'LogInfo %s enter at %r' % (self.ip, self.time_r)

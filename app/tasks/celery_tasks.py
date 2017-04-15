#!/usr/bin/python
# -*- coding:utf-8 -*-

from .. import celery, mail, create_app, db
from flask_mail import Message
import re

@celery.task
def send_email(to, subject, template):
    app = create_app()
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    with app.app_context():
        mail.send(msg)


@celery.task
def get_post_img(post):
    reg = r'<img alt.*?src="(.*?)".*?/>'
    img = re.compile(reg)
    img_list = img.findall(post.body)
    if img_list:
        post_img = ''.join(img_list[0])
    return post_img


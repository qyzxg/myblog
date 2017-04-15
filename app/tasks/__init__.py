# #!/usr/bin/python
# # -*- coding:utf-8 -*-
#
# from .. import create_app, mail
# from flask_mail import Message
# from celery import Celery
#
# def make_celery(app):
#     celery = Celery('tasks', broker=app.config['CELERY_BROKER_URL'])
#     celery.conf.update(app.config)
#     TaskBase = celery.Task
#     class ContextTask(TaskBase):
#         abstract = True
#         def __call__(self, *args, **kwargs):
#             with app.app_context():
#                 return TaskBase.__call__(self, *args, **kwargs)
#     celery.Task = ContextTask
#     return celery
#
# app = create_app()
#
# celery = make_celery(app)
#
# @celery.task
# def send_email(to, subject, template):
#     msg = Message(
#         subject,
#         recipients=[to],
#         html=template,
#         sender=app.config['MAIL_DEFAULT_SENDER']
#     )
#
#     mail.send(msg)
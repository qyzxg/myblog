#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
from fabric.api import *
"""这是一个自动部署脚本
1.远程服务器安装好Python环境/Nginx/gunicorn/redis/mysql
2.对以上进行配置如Nginx配置:
    $ sudo vim /etc/nginx/site-avalidable/default
    server {
    listen 80 default_server;
    listen [::]:80 default_server;
    # 这是HOST机器的外部域名，用地址也行
    server_name example.org;
    location / {
        # 这里是指向 gunicorn host 的服务地址
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
3.初始化数据库
4.将本文件拷贝到和myblog同级目录,如:www,创建deploy目录
    目录结构:
    /www
        myblog
          app
          ...
        fabfile.py
        deploy
5.填写fabric配置信息,在www目录下运行 fab build 打包程序文件,然后运行fab deploy
6.在myblog目录下运行 gunicorn -w 4 -b 127.0.0.1:8080 run:app 
7.完

这只是一个基本部署,还有进程管理等可以自己Google,
该部署流程要求本地计算机为*x平台,window需要在cygwin环境下执行
"""
#fabric配置信息
env.hosts = ['你的服务器IP']
env.key_filename = "你的ssh私钥" #或者env.password='你的服务器ssh密码'
env.user = '服务器登录用户名'
env.sudo_user = '服务器root用户用户名,一般就是root'
db_user = '数据库用户名'
db_password = '数据库密码'


def test():
    with cd('/www'):
        sudo('mkdir hello')


_TAR_FILE = 'myblog.tar.gz'

# 打包
def build():
    includes = ['app', 'logs', 'search', '*.py', '*.txt', 'migrations']
    excludes = ['test', '.idea', 'screenshot', '.*', '*.pyc', '*.pyo', '__pycache__', '.git']
    local('rm -f deploy/%s' % _TAR_FILE)
    with lcd(os.path.join(os.path.abspath('.'), 'myblog')):
        cmd = ['tar', '--dereference', '-czvf', '../deploy/%s' % _TAR_FILE]
        cmd.extend(['--exclude=\'%s\'' % ex for ex in excludes])
        cmd.extend(includes)
        local(' '.join(cmd))


_REMOTE_TMP_TAR = '/www/%s' % _TAR_FILE
_REMOTE_BASE_DIR = '/www'


def deploy():
    # 把打包好的程序源文件上传到远程服务器
    put('deploy/%s' % _TAR_FILE, _REMOTE_TMP_TAR)

    with cd('%s' % _REMOTE_BASE_DIR):
        sudo('rm -rf myblog') #删除上一个版本的程序
        sudo('mkdir myblog')

    with cd('%s/myblog' % _REMOTE_BASE_DIR):
        sudo('mv -f %s .' % _REMOTE_TMP_TAR)
        sudo('tar -xzvf %s' % _TAR_FILE) # 解压
        sudo('rm -f %s' % _TAR_FILE) # 删除压缩包
        sudo('mv -f /www/migrations .')

    with cd('/'):
        sudo('chown -R ubuntu www') #改变权限

    with cd('%s/myblog' % _REMOTE_BASE_DIR):
        sudo('python3 manage.py db migrate')
        sudo('python3 manage.py db upgrade')
        sudo('cp -r migrations ..')
        # 重置软链接:
        # with cd(_REMOTE_BASE_DIR):
        #     sudo('rm -f myblog')
        # sudo('ln -s %s myblog' % newdir)
        # sudo('chown www-data:www-data www')
        # sudo('chown -R www-data:www-data %s' % newdir)
        # 重启Python服务和nginx服务器:
        # with settings(warn_only=True):
        #     sudo('supervisorctl stop awesome')
        #     sudo('supervisorctl start awesome')
        #     sudo('/etc/init.d/nginx reload')

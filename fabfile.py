#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
from fabric.api import *
import datetime

"""这是一个自动部署脚本
1.远程服务器安装好Python环境/Nginx/gunicorn/redis/mysql/supervisor
2.配置Nginx:
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
3.配置supervisor,生成默认配置echo_supervisord_conf > /etc/supervisord.conf
    配置示例:
    [unix_http_server]
    file=/var/run/supervisor.sock   ; the path to the socket file
    
    [supervisord]
    logfile=/var/run/supervisord.log ; main log file; default $CWD/supervisord.log
    logfile_maxbytes=50MB        ; max main logfile bytes b4 rotation; default 50MB
    logfile_backups=10           ; # of main logfile backups; 0 means none, default 10
    loglevel=info                ; log level; default info; others: debug,warn,trace
    pidfile=/var/run/supervisord.pid ; supervisord pidfile; default supervisord.pid
    nodaemon=false               ; start in foreground if true; default false
    minfds=1024                  ; min. avail startup file descriptors; default 1024
    minprocs=200                 ; min. avail process descriptors;default 200
    
    [rpcinterface:supervisor]
    supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface
    
    [supervisorctl]
    serverurl=unix:///var/run/supervisor.sock ; use a unix:// URL  for a unix socket
    
    ;[include]
    ;files = relative/directory/*.ini
    
    [program:myblog]
    command=/usr/local/bin/gunicorn -c /etc/gunicorn.py run:app
    directory=/www/myblog
    user=root
    autostart=true
    autorestart=true
    startsecs = 10
    stdout_logfile = /var/log/gunicorn/debug.log
    
    [program:celeryworker]
    command=/usr/local/bin/celery worker -A celery_worker.celery -l info -c 4 -f /var/log/celery/worker.log
    ;command=/usr/local/bin/celery worker -A celery_worker.celery --loglevel=info -c 4 -f /var/log/celery/worker.log -queues=default,schedule,timing
    directory=/www/myblog
    user=root
    autostart=true
    autorestart=true
    startsecs = 10
    stdout_logfile = /var/log/celery/worker.log
    
    [program:celerybeat]
    command=/usr/local/bin/celery beat -A celery_worker.celery --loglevel=info -f /var/log/celery/beat.log
    directory=/www/myblog
    user=root
    autostart=true
    autorestart=true
    startsecs = 10
    stdout_logfile = /var/log/celery/beat.log
4.进入myblog 运行 sudo pip install -r requirements.txt 安装所有Python包
5.修改config.py等配置文件
6.初始化数据库
    进入 myblog,在终端运行
    from app import db, models, create_app
    app = create_app('default')
    with app.app_context:
        db.create_all()
7.将本文件拷贝到和myblog同级目录,如:www,创建deploy目录
    目录结构:
    /www
        myblog
          app
          ...
        fabfile.py
        deploy
8.填写fabric配置信息,在www目录下运行 fab build 打包程序文件,然后运行fab deploy(运行fab需要bash环境)

提示:
1.数据库迁移进入: myblog 终端运行 python3 manage.py db init, python3 manage.py db migrate, python3 manage.py db upgrade

这只是一个基本部署,具体细节自己Google,
该部署流程要求本地计算机为*x平台,window需要在cygwin环境下执行
"""
# fabric配置信息
# env.hosts = ['你的服务器IP']
# env.key_filename = "你的ssh私钥" #或者env.password='你的服务器ssh密码'
# env.user = '服务器登录用户名'
# env.sudo_user = '服务器root用户用户名,一般就是root'
# db_user = '数据库用户名'
# db_password = '数据库密码'



# 阿里云
env.hosts = ['root@106.14.9.166', 'ubuntu@ec2-13-112-193-37.ap-northeast-1.compute.amazonaws.com']
env.roledefs = {'all': ['root@106.14.9.166', 'ubuntu@ec2-13-112-193-37.ap-northeast-1.compute.amazonaws.com'],
                'aliyun': ['root@106.14.9.166'],
                'aws': ['ubuntu@ec2-13-112-193-37.ap-northeast-1.compute.amazonaws.com']}
env.key_filename = [r'/mnt/d/ymxssh/aliyun.pem', r'/mnt/d/ymxssh/aws.pem']
env.sudo_user = 'root'
db_user = 'root'
db_password = 'qyzxg'
output['stdout'] = False
output['running'] = False
output['status'] = False

_TAR_FILE = 'myblog.tar.gz'
_REMOTE_TMP_TAR = '/www/%s' % _TAR_FILE
_REMOTE_BASE_DIR = '/www'


# 打包
def build():
    print('开始打包...' + '\n')
    includes = ['app', 'logs', '*.py', '*.txt']
    excludes = ['test', '.idea', 'screenshot', '.*', '*.pyc', '*.pyo',
                '__pycache__', 'search', '.git', 'migrations']
    local('rm -f deploy/%s' % _TAR_FILE)
    with lcd(os.path.join(os.path.abspath('.'), 'myblog')):
        cmd = ['tar', '--dereference', '-czvf', '../deploy/%s' % _TAR_FILE]
        cmd.extend(['--exclude=\'%s\'' % ex for ex in excludes])
        cmd.extend(includes)
        local(' '.join(cmd))
    print('打包完毕...' + '\n')


@roles('aliyun')
def deploy():
    # 把打包好的程序源文件上传到远程服务器
    print('开始部署主机{}...'.format(env.host) + '\n')
    print('   00.停止supervisor...' + '\n')
    sudo('supervisorctl shutdown')

    print('   01.上传文件...' + '\n')
    put('deploy/%s' % _TAR_FILE, _REMOTE_TMP_TAR)

    with cd('%s/myblog' % _REMOTE_BASE_DIR):
        print('   02.将search文件夹移动至{}...'.format(_REMOTE_BASE_DIR) + '\n')
        sudo('mv -f search %s' % _REMOTE_BASE_DIR)

    with cd('%s' % _REMOTE_BASE_DIR):
        print('   03.删除上一个版本...' + '\n')
        sudo('rm -rf myblog')  # 删除上一个版本的程序
        print('   04.新建文件夹myblog...' + '\n')
        sudo('mkdir myblog')

    with cd('%s/myblog' % _REMOTE_BASE_DIR):
        print('   05.将{}文件移动至myblog...'.format(_REMOTE_TMP_TAR) + '\n')
        sudo('mv -f %s .' % _REMOTE_TMP_TAR)
        print('   06.解压文件{}...'.format(_REMOTE_TMP_TAR) + '\n')
        sudo('tar -xzvf %s' % _TAR_FILE)  # 解压
        print('   07.删除文件{}...'.format(_REMOTE_TMP_TAR) + '\n')
        sudo('rm -f %s' % _TAR_FILE)  # 删除压缩包
        print('   08.移动文件夹migrations至myblog...' + '\n')
        sudo('mv -f /www/migrations .')
        print('   09.移动文件夹search至myblog...' + '\n')
        sudo('mv -f /www/search .')

    with cd('%s/myblog' % _REMOTE_BASE_DIR):
        print('   10.正在进行数据迁移...' + '\n')
        sudo('python3 manage.py db migrate')
        sudo('python3 manage.py db upgrade')
        print('   11.备份文件夹migrations...' + '\n')
        sudo('cp -r migrations ..')  # 备份migrations文件夹
        print('   12.改变权限...' + '\n')
        sudo('chmod 777 /var/run/')
        sudo('chmod 777 /var/log/')
        print('   13.启动supervisor...' + '\n')
        sudo('supervisord -c /etc/supervisord.conf')

    print('主机{}一切正常,部署完毕!'.format(env.host) + '\n')


def download():
    # 从服务器下载文件
    dir_name = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    with lcd('./deploy/download_files/'):
        local('mkdir %s' % dir_name)
        get('/var/log/nginx/*', './%s' % dir_name)
        # get('/*', './deploy/download_files/sys')


def upload():
    sudo('rm -rf /www/upload_files')
    put('deploy/upload_files', _REMOTE_BASE_DIR)


def clear():
    with cd('/tmp'):
        sudo('rm -rf blogchche')
        run('mkdir blogchche')


@roles('aws')
def shutd():
    sudo('shutdown -r now')
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

### 基本部署方法
系统:Ubuntu16.04
主机:亚马逊EC2/阿里云ECS(推荐EC2免费使用1年,速度还可以,比较稳定)
1. 远程服务器安装好Python环境/Nginx/gunicorn/redis/mysql/supervisor
2. 配置Nginx:

    $ sudo vim /etc/nginx/site-avalidable/default
    
    server {
    listen 80 default_server;
    listen [::]:80 default_server;
    这是HOST机器的外部域名，用地址也行
    server_name example.org;
    location / {
        这里是指向 gunicorn host 的服务地址
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
3. 配置supervisor,生成默认配置echo_supervisord_conf > /etc/supervisord.conf
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
4. 进入myblog 运行 sudo pip install -r requirements.txt 安装所有Python包
5. 修改config.py等配置文件
6. 初始化数据库
    进入 myblog,在终端运行
    from app import db, models, create_app
    app = create_app('default')
    with app.app_context:
        db.create_all()
7. 将本文件拷贝到和myblog同级目录,如:www,创建deploy目录
    目录结构:
    /www
        myblog
          app
          ...
        fabfile.py
        deploy
8. 填写fabric配置信息,在www目录下运行 fab build 打包程序文件,然后运行fab deploy(运行fab需要bash环境)


> 数据库迁移: 进入myblog 终端运行 python3 manage.py db init, python3 manage.py db migrate, python3 manage.py db upgrade
> 注:这只是一个基本部署,还有进程管理等可以自己Google,
> 该部署流程要求本地计算机为Linux平台,window需要在cygwin环境下执行
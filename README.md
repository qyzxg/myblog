### Author:qyzxg
### Email:qyzxg@live.com

### 项目介绍
myblog是一个基于flask的开源多用户博客系统,功能基本完整,目前主要功能如下,代码简单易懂,比较适合作为入门参考:
- [x] 用户注册登录,邮件激活 
- [x] 发表(CKeditor,开启文件上传功能),修改博客,发布评论
- [x] 全文搜索,支持中文搜索
- [x] 文章收藏,文章分类
- [x] 用户关注,用户资料页
- [x] 站内信功能
- [x] 用户后台,修改图像(本地上传),密码,查看个人信息统计(echarts图表),管理自己的文章,评论,好友,消息等
- [x] 管理员后台,查看所有统计信息图表,管理所有文章,评论,用户(权限控制),发布系统通知
- [x] 其他功能,所有celery异步处理电子邮件,获取文章图片,使用redis缓存页面(首页,文章详情页等)和函数(获取图表所需数据的函数)
- [x] 表格排序,搜索,分页选择,批量删除
- [x] 发表评论不刷新加载
- [x] 注册登录验证码功能
- [x] 文章自动采集
- [x] 第三方登录,目前只有qq

### 主要技术和工具
* Python 3.5.2
* flask 0.12
* mysql 5.7
* CKeditor 4.6
* echarts 3.0
* celery
* redis
* Nginx
* gunicorn
* fabric3
* jQuery
* ajax
* datatables
* supervisor

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

### 网站demo部署在阿里云ECS上
* 网址:www.51qinqing.com
* 可以自己注册账号测试,需要管理员账号的请发邮件给我
* 建议自己注册账号测试,欢迎发布文章

### 网站截图

#### 首页
![image](https://github.com/qyzxg/myblog/blob/master/screenshot/首页.png)
#### 文章详情页
![image](https://github.com/qyzxg/myblog/blob/master/screenshot/文章详情页.png)
#### 文章评论
![image](https://github.com/qyzxg/myblog/blob/master/screenshot/文章评论.png)
#### 个人首页
![image](https://github.com/qyzxg/myblog/blob/master/screenshot/个人首页.png)
#### 其他人首页
![image](https://github.com/qyzxg/myblog/blob/master/screenshot/其他人首页.png)
#### 个人博客管理
![image](https://github.com/qyzxg/myblog/blob/master/screenshot/个人博客管理.png)
#### 消息管理
![image](https://github.com/qyzxg/myblog/blob/master/screenshot/消息管理.png)
#### 站内搜索
![image](https://github.com/qyzxg/myblog/blob/master/screenshot/站内搜索.png)
#### 个人博客管理
![image](https://github.com/qyzxg/myblog/blob/master/screenshot/个人博客管理.png)
#### 管理员首页
![image](https://github.com/qyzxg/myblog/blob/master/screenshot/管理员首页.png)
#### 用户管理
![image](https://github.com/qyzxg/myblog/blob/master/screenshot/用户管理.png)
#### 个人博客管理
![image](https://github.com/qyzxg/myblog/blob/master/screenshot/个人博客管理.png)
#### pv/uv统计
![image](https://github.com/qyzxg/myblog/blob/master/screenshot/pv统计.png)
#### 个人博客管理
![image](https://github.com/qyzxg/myblog/blob/master/screenshot/个人博客管理.png)
#### 用户分布
![image](https://github.com/qyzxg/myblog/blob/master/screenshot/用户分布.png)
#### 博客数据统计
![image](https://github.com/qyzxg/myblog/blob/master/screenshot/博客数据统计.png)

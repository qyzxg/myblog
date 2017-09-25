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
- [x] 第三方登录,目前只有qq,GitHub,TODO:微信,微博

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

### 网站demo部署在阿里云ECS上
* 网址:https://www.51qinqing.com
* 可以自己注册账号测试,需要管理员账号的请发邮件给我
* 建议自己注册账号测试,欢迎发布文章

### 网站截图

#### 首页
![image](https://static.51qinqing.com/GitHub/%E9%A6%96%E9%A1%B5.png)
#### 文章详情页
![image](https://static.51qinqing.com/GitHub/%E6%96%87%E7%AB%A0%E8%AF%A6%E6%83%85%E9%A1%B5.png)
#### 文章评论
![image](https://static.51qinqing.com/GitHub/%E6%96%87%E7%AB%A0%E8%AF%84%E8%AE%BA.png)
#### 个人首页
![image](https://static.51qinqing.com/GitHub/%E4%B8%AA%E4%BA%BA%E9%A6%96%E9%A1%B5.png)
#### 其他人首页
![image](https://static.51qinqing.com/GitHub/%E5%85%B6%E4%BB%96%E4%BA%BA%E9%A6%96%E9%A1%B5.png)
#### 个人博客管理
![image](https://static.51qinqing.com/GitHub/%E4%B8%AA%E4%BA%BA%E5%8D%9A%E5%AE%A2%E7%AE%A1%E7%90%86.png)
#### 消息管理
![image](https://static.51qinqing.com/GitHub/%E6%B6%88%E6%81%AF%E7%AE%A1%E7%90%86.png)
#### 站内搜索
![image](https://static.51qinqing.com/GitHub/%E7%AB%99%E5%86%85%E6%90%9C%E7%B4%A2.png)
#### 管理员首页
![image](https://static.51qinqing.com/GitHub/%E7%AE%A1%E7%90%86%E5%91%98%E9%A6%96%E9%A1%B5.png)
#### 用户管理
![image](https://static.51qinqing.com/GitHub/%E7%94%A8%E6%88%B7%E7%AE%A1%E7%90%86.png)
#### pv/uv统计
![image](https://static.51qinqing.com/GitHub/pv%E7%BB%9F%E8%AE%A1.png)
#### 用户分布
![image](https://static.51qinqing.com/GitHub/%E7%94%A8%E6%88%B7%E5%88%86%E5%B8%83.png)
#### 博客数据统计
![image](https://static.51qinqing.com/GitHub/%E5%8D%9A%E5%AE%A2%E6%95%B0%E6%8D%AE%E7%BB%9F%E8%AE%A1.png)

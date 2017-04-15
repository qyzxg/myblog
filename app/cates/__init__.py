#!/usr/bin/python
# -*- coding:utf-8 -*-

#!/usr/bin/python
# -*- coding:utf-8 -*-

"""这个蓝图是专门用来处理文章分类的"""

from flask import Blueprint


cates = Blueprint('cates', __name__)

from . import views

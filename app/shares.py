#!/usr/bin/python
# -*- coding:utf-8 -*-
from functools import wraps
from flask_login import current_user
from flask import flash, redirect, url_for, request
import time
from qiniu import Auth, put_data
import random


def admin_required(f):
    @wraps(f)
    def view_function(*args, **kwargs):
        if not current_user.role == 1:
            flash('您没有管理员权限!')
            next_url = request.args.get('next')
            return redirect(next_url or url_for('public.index'))
        return f(*args, **kwargs)

    return view_function


class UploadToQiniu():
    '''上传文件到七牛'''

    def __init__(self, file, prefix, domian_name='https://static.51qinqing.com', bucket_name='static', expire=3600):
        self.access_key = 'iDfXDpVa4pxFW4tyqkJK8dPkeSeRPlEsGZN7qnST'
        self.secret_key = 'iT3Z4r_z23zauKlyAsTCj51t6WOtJWbADhPKn2O6'
        self.bucket_name = bucket_name
        self.domian_name = domian_name
        self.file = file
        self.expire = expire
        self.prefix = prefix

    def upload(self):
        user = current_user
        ext = self.file.filename.split('.')[-1]
        time_ = str(time.time()).replace('.', '')
        k = self.prefix + time_ + '_' + str(user.id) + '.' + ext
        q = Auth(self.access_key, self.secret_key)
        token = q.upload_token(self.bucket_name, k, self.expire)
        return put_data(token, k, self.file.read())

    def upload_web(self, file_name, file):
        q = Auth(self.access_key, self.secret_key)
        token = q.upload_token(self.bucket_name, file_name, self.expire)
        return put_data(token, self.prefix + file_name, file)


class DFAFilter():
    '''Filter Messages from keywords
    Use DFA to keep algorithm perform constantly
    f = DFAFilter()
    f.add("sexy")
    f.filter("hello sexy baby")
    hello **** baby
    '''

    def __init__(self):
        self.keyword_chains = {}
        self.delimit = '\x00'

    def add(self, keyword):
        keyword = keyword.lower()
        chars = keyword.strip()
        if not chars:
            return
        level = self.keyword_chains
        for i in range(len(chars)):
            if chars[i] in level:
                level = level[chars[i]]
            else:
                if not isinstance(level, dict):
                    break
                for j in range(i, len(chars)):
                    level[chars[j]] = {}
                    last_level, last_char = level, chars[j]
                    level = level[chars[j]]
                last_level[last_char] = {self.delimit: 0}
                break
        if i == len(chars) - 1:
            level[self.delimit] = 0

    def parse(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            for keyword in f.readlines():
                self.add(keyword.strip())

    def filter(self, message, repl="*"):
        message = message.lower()
        ret = []
        start = 0
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            for char in message[start:]:
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:
                        level = level[char]
                    else:
                        ret.append(repl * step_ins)
                        start += step_ins - 1
                        break
                else:
                    ret.append(message[start])
                    break
            else:
                ret.append(message[start])
            start += 1
        return ''.join(ret)


def do_pagination(query, per_page=10):
    '''封装分页功能'''
    page_index = request.args.get('page', 1, type=int)
    pagination = query.paginate(page_index, per_page=per_page, error_out=False)
    items = pagination.items
    return pagination, items


img_list = [
    '1304525430-0.jpg',
    '032013yUu.jpg',
    '10772877275_bd4d764325_b.jpg',
    '11801452763_50dde53de2_b.jpg',
    '13241598423_9f492cacb6_b.jpg',
    '6946443124_5bd6c88e9e_b.jpg',
    '13822577795_5cd31f464a_b.jpg',
    '11340601525_0b09f1133d_b.jpg',
    '18212504776_40fe6548e2_b.jpg',
    '20471528443_e39d992210_b.jpg',
    '23606693854_a6b3fb86c2_b.jpg',
    '28305390372_d3bd5fe460_b.jpg',
    '28629559405_1f471929ce_b.jpg',
    '29932753623_f9b8a4db63_b.jpg',
    '30616861736_baa4b5e0a9_b.jpg',
    '31397302444_cba4f0824d_b.jpg',
    '18910440381_52fa9fe432_b.jpg',
    'Materials19.jpg',
    'apic14052.jpg',
    '20140827184301734.jpg',
    'Materials23.jpg',
    'Materials12.jpg',
    'Materials31.jpg',
    'Materials27.jpg',
    'Materials33.jpg',
    'Materials38.jpg',
    'Materials41.jpg',
    'Materials44.jpg',
    'Materials164.jpg'
]

def choice_img():
    return 'https://static.51qinqing.com/postimg/' + random.choice(img_list)
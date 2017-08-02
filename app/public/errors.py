#!/usr/bin/python
# -*- coding:utf-8 -*-

from flask import render_template, request, jsonify
from . import public


# @public.app_errorhandler(403)
# def forbidden(e):
#     if request.accept_mimetypes.accept_json and \
#             not request.accept_mimetypes.accept_html:
#         response = jsonify({'error': 'forbidden'})
#         response.status_code = 403
#         return response
#     return render_template('403.html'), 403


@public.app_errorhandler(404)
def page_not_found(error):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('public/404.html'), 404


@public.app_errorhandler(403)
def internal_server_error(error):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'forbidden'})
        response.status_code = 403
        return response
    return render_template('public/403.html'), 403


@public.app_errorhandler(500)
def internal_server_error(error):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    return render_template('public/500.html'), 500

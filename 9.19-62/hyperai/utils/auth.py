# Copyright (c) 2015-2017, NVIDIA CORPORATION.  All rights reserved.
# coding=utf-8
from __future__ import absolute_import

# import flask
import functools
import re
import werkzeug.exceptions
from flask import redirect,request,session,g
from .routing import get_request_arg, request_wants_json


def get_username():
    return get_request_arg('username') or \
           request.cookies.get('username', None)


def validate_username(username):
    """
    Raises a ValueError if the username is invalid
    """
    if not username:
        raise ValueError('username is required')
    if not re.match('[a-z]', username):
        raise ValueError('Must start with a lowercase letter')
    if not re.match('[a-z0-9\.\-_]+$', username):
        raise ValueError('Only lowercase letters, numbers, periods, dashes and underscores allowed')


# def requires_login(f=None, redirect=True):
#     """
#     Decorator for views that require the user to be logged in
#
#     Keyword arguments:
#     f -- the function to decorate
#     redirect -- if True, this function may return a redirect
#     """
#     if f is None:
#         # optional arguments are handled strangely
#         return functools.partial(requires_login, redirect=redirect)
#
#     @functools.wraps(f)
#     def decorated(*args, **kwargs):
#         username = get_username()
#         if not username:
#             # Handle missing username
#             if request_wants_json() or not redirect:
#                 raise werkzeug.exceptions.Unauthorized()
#             else:
#                 return flask.redirect(flask.url_for('hyperai.views.login', next=flask.request.path))
#         try:
#             # Validate username
#             validate_username(username)
#         except ValueError as e:
#             raise werkzeug.exceptions.BadRequest('Invalid username - %s' % e.message)
#         return f(*args, **kwargs)
#
#     return decorated


def has_permission(job, action, username=None):
    """
    Returns True if username can perform action on job
    如果用户名可以对job进行操作 返回True
    Arguments:
    job -- the Job in question
    action -- the action in question

    Keyword arguments:
    username -- the user in question (defaults to current user)
    """
    if job.is_read_only():
        return False

    if username is None:
        username = get_username()

    if not username:
        return False
    if not job.username:
        return True
    return username == job.username


# 验证登录函数

def requires_login(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        username = request.cookies.get('username')
        if username is None:
            return redirect('/user/login')
        else:
            return func(*args, **kwargs)

    return wrapper

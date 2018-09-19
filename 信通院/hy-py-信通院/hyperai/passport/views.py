# -*- coding: utf-8 -*-

from __future__ import absolute_import
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import logging
import os
from flask import Blueprint, request, jsonify, render_template, session, url_for, redirect, make_response

from hyperai.ext import db  # 导入数据库 进行存储
from hyperai.models import User,Department
from hyperai.utils.get_hash import get_hash
from hyperai.utils.response_code import RET
from hyperai.webapp import scheduler
from hyperai.config import config_value
from flask import Flask
from flask_mail import Mail, Message
# logger.info('Database created after %d seconds.' % (time.time() - start))
# 蓝图注册
blueprint = Blueprint(__name__, __name__)

logger = logging.getLogger('hyperai.passport')  # 生成日志文件

# app = Flask(__name__)
# app.config.update(dict(
#       DEBUG = True,
#       MAIL_SERVER = 'smtp.163.com',
#       MAIL_PORT = 465,
#       MAIL_USE_TLS = False,
#       MAIL_USE_SSL = True,
#       MAIL_PASSWORD = config_value('mail_password'),
#       MAIL_USERNAME = config_value('mail_username')
#   ))
#
# mail = Mail(app)




# /user/register
@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        """注册用户"""
        # 接收前台数据
        name = request.form.get('username')
        pwd = request.form.get('pwd')
        department = request.form.get('department')
        print department
        depart_name = department.split('/')[1]

        real_name = request.form.get('real_name').encode('utf-8')
        phone = request.form.get('phone')
        email = request.form.get('email')
        release = False

        if not all([name, pwd, department, phone, email]):
            return jsonify(errno=RET.PARAMERR, errmsg='param')
        # 存储用户信息
        if name == 'Administrator':
            examined = True
        else:
            examined = False
        user = User(name=name, password=get_hash(pwd), real_name=real_name, phone=phone,
                    email=email, examined=examined, release=release)
        db.session.add(user)
        depart = Department.query.filter_by(depart_name=depart_name).first()
        user.departments.append(depart)
        # try:
        #     # 提交数据
        #     if os.path.exists(os.path.join(config_value('jobs_dir'),name)):
        #         pass
        #         user_add = 'useradd ' + name
        #         os.system(user_add)
        #     else:
        #         os.makedirs(os.path.join(config_value('jobs_dir'), name + '/code'))
        #         os.makedirs(os.path.join(config_value('jobs_dir'), name + '/data'))
        #         os.makedirs(os.path.join(config_value('jobs_dir'), name + '/jobs'))
        #         os.makedirs(os.path.join(config_value('jobs_dir'), name + '/infer'))
        #         user_add = 'useradd ' + name
        #         os.system(user_add)
        #         print 'dirs create successfully'
        #
        #     db.session.commit()
        # except Exception as e:
        #     print e
        #     db.session.rollback()
        try:
            db.session.commit()
            # msg = Message('审批请求', sender=config_value('mail_username'), \
            #               recipients=[config_value('mail_username')])
            # msg.body = 'From register!'
            # msg.html = '<b>' + name + '已经注册，请求通过审批！</b>'
            # with app.app_context():
            #     mail.send(msg)
        except Exception as e:
            db.session.rollback()
        return redirect(url_for('hyperai.passport.views.login'))
    elif request.method == 'GET':
        all_depart = Department.query.all()
        return render_template('new/reg.html', all_depart=all_depart)


# /user/name
@blueprint.route('/name', methods=['POST'])
def name():
    name = request.form.get('name')
    try:
        user = User.query.filter_by(name=name).first()
    except Exception as e:
        logger.error(e)
    if user:
        return jsonify({'res': 1})  # 帐号被注册
    else:
        return jsonify({'res':0})


# /user/login

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('/new/login1.html')
    elif request.method == 'POST':
        name = request.form.get('name')
        pwd = request.form.get('pwd')
        user = User.query.filter_by(name=name).first()

        if user is None:
            return jsonify({'res': 2})  # 用户名已注册
        if not all([name, pwd]):
            return jsonify(errno=RET.PARAMERR, errmsg='paramerr')
        try:
            user = User.query.filter_by(name=name, password=get_hash(pwd)).first()
        except Exception as e:
            logger.error(e)

        if user is None:
            return jsonify({'res': 3})  # 密码或用户名错误返回3
        examined = user.examined
        if examined: # False为审批中  Ture为审批通过
            # 缓存当前用户信息
            session['islogin'] = True
            response = make_response(jsonify({'res':1}))
            response.set_cookie('username', user.name,max_age=7200)
            user_path = os.path.join(config_value('jobs_dir'),name)
            if os.path.exists(user_path):
                pass
            else:
                os.makedirs(user_path)
                os.makedirs(os.path.join(config_value('jobs_dir'), name + '/code'))
                os.makedirs(os.path.join(config_value('jobs_dir'), name + '/data'))
                os.makedirs(os.path.join(config_value('jobs_dir'), name + '/jobs'))
                os.makedirs(os.path.join(config_value('jobs_dir'), name + '/infer'))
            return response
        else:
            return jsonify({'res':4})

#/user/logut
@blueprint.route('/logout',methods=['GET','POST'])
def logout():

    response = make_response(redirect('/user/login'))
    response.set_cookie('username','')
    return response


@blueprint.route('/forget_password',methods=['GET','POST'])
def forget_password():
    if request.method == 'GET':
        return render_template('new/retrievePassword.html')
    elif request.method == 'POST':
        username = request.form.get('user')
        phone = request.form.get('verify')
        user = User.query.filter_by(name=username).first()
        if user is None:
            return jsonify({'res': 2})  # 用户名不存在
        elif user.phone != phone:
            return jsonify({'res': 1})  # 手机号验证出错
        return jsonify({'res': 0})  # 验证成功


@blueprint.route('/update_password', methods=['POST'])
def update_password():
    if request.method == 'POST':
        username = request.form.get('user')
        pwd = request.form.get('password')
        password = get_hash(pwd)
        user = User.query.filter_by(name=username).first()
        user.password = password
        db.session.add(user)
        db.session.commit()
        return jsonify({'res': 1})  # 修改成功


# email
@blueprint.route('/email', methods=['POST'])
def email():
    email = request.form.get('email')
    try:
        user_email = User.query.filter_by(email=email).first()
    except Exception as e:
        logger.error(e)
    if user_email:
        return jsonify({'res': 1})  # 邮箱不可用
    else:
        return jsonify({'res':0})


# coding=utf-8
# Copyright (c) 2014-2017, NVIDIA CORPORATION.  All rights reserved.
from __future__ import absolute_import

import glob
import json
import platform
import traceback
import re
import os
import json
import shutil
import threading
from datetime import datetime

import flask
from flask.ext.socketio import join_room, leave_room
from werkzeug import HTTP_STATUS_CODES
import werkzeug.exceptions
from flask import request
from .config import config_value
from .webapp import app, socketio, scheduler
import hyperai
from hyperai import dataset, extensions, model, utils, pretrained_model, vip, tuning
from hyperai.log import logger
from hyperai.utils.routing import request_wants_json
from hyperai.models import User, Dataset, Model, Department
from hyperai.ext import db
from hyperai.dataset import images as dataset_images
from hyperai.model.images.generic.views import get_data_extensions,get_view_extensions
from collections import Counter
import math
from .vip import DistributedJob
from .tuning import ParaJob
from hyperai.utils.auth import requires_login
# from hyperai.ext import r
from hyperai.utils.get_hash import get_hash
from hyperai.tools.deploy.kube import KubernetasCoord as k8s
from hyperai.users import register_user
blueprint = flask.Blueprint(__name__, __name__)


@blueprint.route('/', methods=['GET'])
@requires_login
def home():
    return flask.redirect('/user/login')

@blueprint.route('/user_manage', methods=['GET'])
@requires_login
def user_manage():
    return flask.render_template('new/user_administrator.html', index='manage')


@blueprint.route('/user_manage_load', methods=['GET', 'POST'])
@requires_login
def user_manage_load():
    size = 10
    if request.method == 'GET':  # 跳转方式进入 默认第一页
        examined_page = 1  # 页面当前点击页码
        no_examined_page = 1  # 页面当前点击页码
    elif request.method == 'POST':  # 点击页数
        examined_page = int(request.form.get('num', 1))  # 页面当前点击页码
        no_examined_page = int(request.form.get('num', 1))  # 页面当前点击页码
    no_examined_user = User.query.filter_by(examined=False).order_by(User.update_time.desc()).all()
    no_examined_length = len(no_examined_user)
    no_examined_pages = get_total_pages(size, no_examined_length)
    no_examined = []
    no_examined_user_name  = []
    for no_examined in no_examined_user:
        no_examined_user_dict = {}
        no_examined_user_dict['id'] = no_examined.id
        no_examined_user_dict['name'] = no_examined.name
        # depart = Department.query.filter_by(Department.id == examined)
        depart = no_examined.departments.first()
        # no_examined_user_dict['department'] = no_examined.get_depart(no_examined.name)
        no_examined_user_dict['department'] = depart.depart_name
        no_examined_user_name.append(no_examined_user_dict)
    if no_examined_page == 1:
        no_examined = no_examined_user_name[0:size]
    else:
        no_examined = no_examined_user_name[(no_examined_page - 1) * size:(no_examined_page * size)]
    examined_user = User.query.filter_by(examined=True).order_by(User.update_time.desc()).all()
    examined_length = len(examined_user)
    examined_user_name = []
    for examined in examined_user:
        examined_user_dict = {}
        if examined.name == "Administrator":
            pass
        else:
            examined_user_dict['id'] = examined.id
            examined_user_dict['name'] = examined.name
            # depart = Department.query.filter_by(Department.id == examined)
            depart = examined.departments.first()
            # examined_user_dict['department'] = examined.get_depart(examined.name)
            examined_user_dict['department'] = depart.depart_name
            # print examined.get_depart(examined.name)
            examined_user_dict['phone'] = examined.phone
            examined_user_dict['email'] = examined.email
            examined_user_name.append(examined_user_dict)
    # print examined_user_name
    examined_pages = get_total_pages(size, examined_length-1)
    examined = []
    if examined_page == 1:
        examined = examined_user_name[0:size]
    else:
        examined = examined_user_name[(examined_page - 1) * size:(examined_page * size)]
    # res.append(no_examined_user)
    # res.append(examined_user)
    return flask.jsonify({
        'no_examined_user': no_examined,
        'no_examined_pages': no_examined_pages,
        'examined_user': examined,
        'examined_pages': examined_pages,
    })

    # return flask.render_template('new/user_administrator.html', res=res,)


def get_total_pages(size,length):
    if length%size == 0:
        pages = length/size
    else:
        pages = (length/size)+1
    return pages


@blueprint.route('/user_examined', methods=['POST'])
@requires_login
def user_examined():
    user_id = request.form.get('user_id')
    user = User.query.filter_by(id=user_id).first()
    user.examined = True
    db.session.add(user)
    try:
        # 提交数据
        if os.path.exists(os.path.join(config_value('jobs_dir'), user.name)):
            pass
            user_add = 'useradd ' + user.name
            os.system(user_add)
        else:
            os.makedirs(os.path.join(config_value('jobs_dir'), user.name + '/code'))
            os.makedirs(os.path.join(config_value('jobs_dir'), user.name + '/data'))
            os.makedirs(os.path.join(config_value('jobs_dir'), user.name + '/jobs'))
            os.makedirs(os.path.join(config_value('jobs_dir'), user.name + '/infer'))
            user_add = 'useradd ' + user.name
            os.system(user_add)
            print 'dirs create successfully'

        db.session.commit()
    except Exception as e:
        print e
        db.session.rollback()
    # db.session.commit()
    return flask.jsonify({
        'errmsg': "ok",
        'id': user_id,
    })


@blueprint.route('/user_noexamined', methods=['POST'])
@requires_login
def user_noexamined():
    user_id = request.form.get('user_id')
    user = User.query.filter_by(id=user_id).first()
    db.session.delete(user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    return flask.jsonify({
        'errmsg': "ok",
        'id': user_id,
    })


@blueprint.route('/user_delete', methods=['POST'])
@requires_login
def user_delete():
    # username = request.form.get('user_id')
    user_ids = request.form.getlist('user_id[]')
    for user_id in user_ids:
        user = User.query.filter_by(id=user_id).first()
        db.session.delete(user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    return flask.jsonify({
        'errmsg': "ok",
    })



@blueprint.route('/user_add', methods=['POST'])
@requires_login
def user_add():
    user_name = request.form.get('user_name')
    user_department = request.form.get('user_depart')
    user_email = request.form.get('user_email')
    user_phone = request.form.get('user_phone')
    if not all([user_name, user_department, user_phone, user_email]):
        return flask.jsonify({
            'errmsg': "param",
        })
        # return flask.jsonify(errmsg='param')
    user = User(name=user_name, password=get_hash("123456"), real_name="", phone=user_phone,
                email=user_email, examined=True)
    db.session.add(user)
    depart = Department.query.filter_by(depart_name=user_department).first()
    user.departments.append(depart)
    try:
        # 提交数据
        if os.path.exists(os.path.join(config_value('jobs_dir'), user_name)):
            pass
            user_add = 'useradd ' + user_name
            os.system(user_add)
        else:
            os.makedirs(os.path.join(config_value('jobs_dir'), user_name + '/code'))
            os.makedirs(os.path.join(config_value('jobs_dir'), user_name + '/data'))
            os.makedirs(os.path.join(config_value('jobs_dir'), user_name + '/jobs'))
            os.makedirs(os.path.join(config_value('jobs_dir'), user_name + '/infer'))
            user_add = 'useradd ' + user_name
            os.system(user_add)
            print 'dirs create successfully'

        db.session.commit()
    except Exception as e:
        print e
        db.session.rollback()

    return flask.jsonify({
        'errmsg': "ok",
    })


@blueprint.route('/user_update', methods=['POST'])
@requires_login
def user_update():
    # user_name = request.form.get('user_name')
    user_id = request.form.get('user_id')
    user = User.query.filter_by(id=user_id).first()

    user.email = request.form.get('email')
    user.phone = request.form.get('phone')


    user_department = request.form.get('depart_name')
    depart = Department.query.filter_by(depart_name=user_department).first()
    # user.departments.first().depart_name = user_department
    # user.departments = None
    user.departments.remove(user.departments.first())
    # user.departments.append(depart)
    # print user.departments.first().
    user.departments.append(depart)
    gpu_used = depart.gpu_max
    # if user.release:
    #     r.set("{}_gpu".format(user.name), gpu_used)
    # else:
    #     if r.get("{}_gpu".format(user.name)) is not None:
    #         if int(r.get("{}_gpu".format(user.name))) > gpu_used:
    #             print "cvcvcv"
    #             r.set("{}_gpu".format(user.name), gpu_used)


    db.session.add(user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()

    return flask.jsonify({
        'errmsg': "ok",
        'user_id': user_id,
    })


@blueprint.route('/department_name', methods=['POST'])
def name():
    name = request.form.get('name')
    try:
        depart = Department.query.filter_by(depart_name=name).first()
    except Exception as e:
        logger.error(e)
    if depart:
        return jsonify({'res': 1})  # 帐号被注册
    else:
        return jsonify({'res':0})


@blueprint.route('/department_load', methods=['GET', 'POST'])
@requires_login
def department_load():
    size = 10
    if request.method == 'GET':  # 跳转方式进入 默认第一页
        department_page = 1  # 页面当前点击页码
    elif request.method == 'POST':  # 点击页数
        department_page = int(request.form.get('num', 1))  # 页面当前点击页码
    departments = Department.query.filter_by().order_by(Department.update_time.desc()).all()
    department_length = len(departments)
    department_pages = get_total_pages(size, department_length)
    department_list = []
    for department in departments:
        department_dict = {}
        department_dict['id'] = department.id
        department_dict['name'] = department.depart_name
        department_dict['power'] = department.depart_power
        department_dict['gpu'] = department.gpu_max
        department_list.append(department_dict)
    if department_page == 1:
        department_list = department_list[0:size]
    else:
        department_list = department_list[(department_page - 1) * size:(department_page * size)]
    return flask.jsonify({
        'department_list': department_list,
        'department_page': department_pages,
    })


@blueprint.route('/department_add', methods=['POST'])
@requires_login
def department_add():
    department_name = request.form.get('depart_name')
    department_power = request.form.get('priority')
    gpu_max = request.form.get('depart_gpu')
    if not all([department_name, department_power, gpu_max]):
        return flask.jsonify({
            'errmsg': "param",
        })
    depart = Department(depart_name=department_name, depart_power=department_power, gpu_max=gpu_max, )
    db.session.add(depart)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    return flask.jsonify({
        'errmsg': "ok",
    })


@blueprint.route('/department_update', methods=['POST'])
@requires_login
def department_update():
    department_id = request.form.get('id')
    depart = Department.query.filter_by(id=department_id).first()
    depart.depart_power = request.form.get('priority')
    depart.gpu_max = request.form.get('gpu')
    db.session.add(depart)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    return flask.jsonify({
        'errmsg': "ok",
        'depart_id': department_id,
    })


@blueprint.route('/department_delete', methods=['POST'])
@requires_login
def department_delete():
    department_id = request.form.get('id')
    depart = Department.query.filter_by(id=department_id).first()
    # print depart.departments.first()
    if depart.departments.first() == None:
        db.session.delete(depart)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
        return flask.jsonify({
            'errmsg': "ok",
            'department_id': department_id,
        })
    else:
        return flask.jsonify({
            'errmsg': '部门被用户占用，不可以删除！',
        })


@blueprint.route('/department_details', methods=['GET'])
@requires_login
def department_details():
    #depart_id = request.form.get('depart_id')
   # print depart_id
    return flask.render_template('new/depart-detail.html')


@blueprint.route('/department_load_user', methods=['GET', 'POST'])
@requires_login
def department_load_user():
    size = 10
    if request.method == 'GET':  # 跳转方式进入 默认第一页
        users_page = 1  # 页面当前点击页码
    elif request.method == 'POST':  # 点击页数
        users_page = int(request.form.get('num', 1))  # 页面当前点击页码
    depart_id = request.form.get('depart_id')
    depart = Department.query.filter_by(id=depart_id).first()
    gpu_max = depart.gpu_max
    power = depart.depart_power
    users = depart.departments.order_by(User.update_time.desc()).all()
    users_length = len(users)
    users_pages = get_total_pages(size, users_length)
    user_list = []
    for user in users:
        user_dict = {}
        if user.name == "Administrator":
            pass
        else:
            user_dict['id'] = user.id
            user_dict['name'] = user.name
            if user.release:
                user_gpu_max = 0
                gpu_used = 0
            else:
                user_gpu_max = gpu_max
                gpu_used = register_user.get_used_resource_about_user(user.name)

                # user_gpu_max = gpu_max
                # if r.get("{}_gpu".format(user.name)) is not None:
                #     gpu_used = r.get("{}_gpu".format(user.name))
                # else:
                #     gpu_used = 0
            user_dict['gpu_used'] = int(user_gpu_max) - int(gpu_used)
            user_dict['user_gpu_max'] = user_gpu_max
            user_list.append(user_dict)
    if users_page == 1:
        user_list = user_list[0:size]
    else:
        user_list = user_list[(users_page - 1) * size:(users_page * size)]
    return flask.jsonify({
        'user_list': user_list,
        'power': power,
        'gpu_max': gpu_max,
        'user_page': users_pages
    })


# @blueprint.route('/user_release', methods=['POST'])
# @requires_login
# def user_release():
#     user_id = request.form.get('user_id')
#     user = User.query.filter_by(id=user_id).first()
#     gpu_used = user.departments.first().gpu_max
#     r.set("{}_gpu".format(user.name), gpu_used)
#     user.release = True
#     db.session.add(user)
#     try:
#         db.session.commit()
#     except Exception as e:
#         db.session.rollback()
#     if scheduler.abort_running_jobs(user.name):
#         print "终止。。。。"
#     deployment_job = scheduler.abort_deployment_jobs(user.name)
#     for deployment in deployment_job:
#         job = scheduler.get_job(deployment)
#         job.job_status = 'Error'
#         yaml_path = os.path.join(config_value('jobs_dir'), user.name + '/jobs', deployment, deployment + '.yaml')
#         k8s.delete_deployment(yaml_path=yaml_path)
#         # k8s.delete_svc(job_id=job_id)
#         # release_res_about_user(job_id)
#         job.tasks[0].relase_gpu_resoures()
#         job.tasks[0].relase_gpu_resoures_about_usr()
#         scheduler.delete_job(deployment)
#     user = User.query.filter_by(id=user_id).first()
#     gpu_used = user.departments.first().gpu_max
#     return flask.jsonify({
#         'user_id': user_id,
#         'gpu_max': 0,
#         'gpu_use': int(user.departments.first().gpu_max)-int(gpu_used),
#     })
#     # user.departments.remove(user.departments.first())


@blueprint.route('/user_release', methods=['POST'])
@requires_login
def user_release():
    user_id = request.form.get('user_id')
    user = User.query.filter_by(id=user_id).first()
    gpu_used = user.departments.first().gpu_max
    user.release = True
    db.session.add(user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    if scheduler.abort_running_jobs(user.name):
        print "终止。。。。"
    deployment_job = scheduler.abort_deployment_jobs(user.name)
    for deployment in deployment_job:
        job = scheduler.get_job(deployment)
        job.job_status = 'Error'
        yaml_path = os.path.join(config_value('jobs_dir'), user.name + '/jobs', deployment, deployment + '.yaml')
        k8s.delete_deployment(yaml_path=yaml_path)
        # k8s.delete_svc(job_id=job_id)
        # release_res_about_user(job_id)
        job.tasks[0].relase_gpu_resoures()
        job.tasks[0].relase_gpu_resoures_about_usr()
        scheduler.delete_job(deployment)
    user = User.query.filter_by(id=user_id).first()
    gpu_used = user.departments.first().gpu_max
    return flask.jsonify({
        'user_id': user_id,
        'gpu_max': 0,
        'gpu_use': int(user.departments.first().gpu_max)-int(gpu_used),
    })
    # user.departments.remove(user.departments.first())


@blueprint.route('/user_restore', methods=['POST'])
@requires_login
def user_restore():
    user_id = request.form.get('user_id')
    # user_id = 23
    user = User.query.filter_by(id=user_id).first()
    gpu_max = user.departments.first().gpu_max
    # if r.get("{}_gpu".format(user.name)) is not None:
    #     gpu_used = r.get("{}_gpu".format(user.name))
    # else:
    gpu_used = 0
    # r.set("{}_gpu".format(user.name), 0)
    user.release = False
    db.session.add(user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    return flask.jsonify({
        'user_id': user_id,
        'gpu_max': gpu_max,
        'gpu_use': int(gpu_max) - int(gpu_used),
    })


@blueprint.route('/get_cmodel', methods=['GET','POST'])
@requires_login
def get_cmodel():
    username = flask.request.cookies.get('username')
    completed_models_old = get_job_list(model.ModelJob, False)
    completed_models = []

    for job in completed_models_old:
        if job.status.name == "Done":
            completed_models.append(job)


    user_models = []

    user = User.query.filter_by(name=username).first()
    model_m_s = user.models.all()
    for u_model in completed_models:
        if u_model.username == username and u_model.owner == True:
            user_models.append(u_model)
    for model_m in model_m_s:
        model_m_job = scheduler.get_job(model_m.job_id)
        user_models.append(model_m_job)

    user_models = list(set(user_models)) # 用户所拥有的模型
         # 用户拥有模型的个数
    model_type = flask.request.form.get('value')
    type_models = []
    for u_model in user_models: # 遍历用户模型  获取每个场景的模型
        if u_model:
            if u_model.apply_scence == model_type and u_model.status == 'D':
                type_models.append([u_model.name(), u_model.id()])

    length = len(type_models)
    return flask.jsonify({'length': length, 'model': type_models})


@blueprint.route('/get_cmodel/detail', methods=['GET','POST'])
@requires_login
def get_model_detail():
    job_id = flask.request.form.get('value')
    job = scheduler.get_job(job_id)

    if job.apply_scence == 'classification':
        weight = job.dataset.image_dims[0]
        height = job.dataset.image_dims[1]
        job.size = str(weight) + 'X' + str(height)
        if job.dataset.parse_folder_tasks():
            train_count = job.dataset.parse_folder_tasks()[0].train_count
            val_count = job.dataset.parse_folder_tasks()[0].val_count
        else:
            train_count = job.dataset.create_db_tasks()[0].entries_count
            val_count = job.dataset.create_db_tasks()[1].entries_count
        image_type = job.dataset.image_dims[2]
    else:
        job.size = None
        job.network = 'custom' if job.network == 'custom' else job.network
        job.dataset.image_dims = None
        if job.apply_scence != 'other':
            train_count = job.dataset.create_db_tasks()[0].entry_count
            val_count = job.dataset.create_db_tasks()[1].entry_count
        else:
            train_count = None
            val_count = None
        image_type = None
    info = {
        'auth': job.username,
        'create_time': job.create_time,
        'apply_scence': job.apply_scence,
        'framework': job.train_task().get_framework_id(),
        'network': job.network,
        'dataset': job.dataset.name(),
        'database': job.dataset.get_backend(),
        'image_type': image_type,
        'train_count': train_count,
        'val_count': val_count,
        'run_time': job.runtime_of_tasks(),
        'size': job.size,
        'job_id': job.id(),
    }
    return flask.jsonify(info)


@blueprint.route('/datasets', methods=['GET'])
@requires_login
def datasets():
    username = flask.request.cookies.get('username')
    user_datasets = get_user_datasets(username,True)
    show_shouye_status = 0  # 显示首页状态
    apply_scence = flask.request.args.get('apply_scence', 'default').lower()
    layout = flask.request.args.get('layout', 'default').lower()
    p = flask.request.args.get("p", '')  # 页数
    if p == '':
        p = 1
    else:
        p = int(p)
        if p > 1:
            show_shouye_status = 1
    name = flask.request.args.get('name', None)
    s_dataset = []
    filter_list = []
    if apply_scence == 'default' and layout == 'default':
        pass
    else:
        print filter_list
        if apply_scence != 'default' and apply_scence != '':
            filter_list.append(apply_scence)
        if layout != 'default' and layout != '':
            filter_list.append(layout)
        if len(filter_list) == 0:
            pass
        elif len(filter_list) == 1:
            for i in user_datasets:
                if i.apply_scence in filter_list or i.get_backend() in filter_list:
                    s_dataset.append(i)
            user_datasets = s_dataset
        elif len(filter_list) == 2:
            for i in user_datasets:
                if i.apply_scence in filter_list and i.get_backend() in filter_list:
                    s_dataset.append(i)
            user_datasets = s_dataset
    if name:
        pattern = '.*'.join(name)  # Converts 'djm' to 'd.*j.*m'
        regex = re.compile(pattern)  #

        for dataset in user_datasets:
            if regex.search(dataset.name()):
                s_dataset.append(dataset)
        user_datasets = s_dataset
    length = len(user_datasets)
    for j in range(length - 1):
        for i in range(length - 1):
            if user_datasets[i].create_time_c < user_datasets[i + 1].create_time_c:
                user_datasets[i], user_datasets[i + 1] = user_datasets[i + 1], user_datasets[i]
    count = len(user_datasets)
    total = int(math.ceil(count / 10.0))  # 总页数

    dic = get_page(total, p)
    datas = {
        'p': int(p),
        'total': total,
        'show_shouye_status': show_shouye_status,
        'dic_list': dic,
        'user_datasets': user_datasets[(p - 1) * 10:p * 10],

    }
    return flask.render_template(
        'new/dataManage.html',
        user_datasets=user_datasets,
        index='dataset',datas=datas,apply_scence=apply_scence,layout=layout
    )


def get_user_datasets(username, status):
    running_datasets = get_job_list(dataset.DatasetJob, True)
    completed_datasets = get_job_list(dataset.DatasetJob, False)
    all_datasets = running_datasets + completed_datasets
    try:
        user = User.query.filter_by(name=username).first()
        dataset_m = user.datasets.all()
    except Exception as e:
        # print e
        return flask.redirect('/user/login')
    user_datasets = []
    if status:
        for data in all_datasets:
            if data.username == username and data.owner == True and data.status == 'D':
                user_datasets.append(data)
        for data_m in dataset_m:
            data_m_job = scheduler.get_job(data_m.job_id)
            if data_m_job and data_m_job.status == 'D':
                user_datasets.append(data_m_job)
    else:
        for data in all_datasets:
            if data.username == username and data.owner == True:
                user_datasets.append(data)
        for data_m in dataset_m:
            data_m_job = scheduler.get_job(data_m.job_id)
            if data_m_job:
                user_datasets.append(data_m_job)
    user_datasets = list(set(user_datasets))
    return user_datasets


def get_user_models(username,status):
    running_models = get_job_list(model.ModelJob, True)
    completed_models = get_job_list(model.ModelJob, False)
    try:
        user = User.query.filter_by(name=username).first()
        model_m_s = user.models.all()
    except Exception as e:
        # print e
        return flask.redirect('/user/login')
    user_models = []
    all_models = running_models + completed_models
    if status:
        for u_model in all_models:
            if u_model.username == username and u_model.owner == True and u_model.status == 'D':
                user_models.append(u_model)
        for model_m in model_m_s:
            model_m_job = scheduler.get_job(model_m.job_id)
            if model_m_job and model_m_job.status == 'D':
                user_models.append(model_m_job)
    else:
        for u_model in all_models:
            if u_model.username == username and u_model.owner == True:
                user_models.append(u_model)
        for model_m in model_m_s:
            model_m_job = scheduler.get_job(model_m.job_id)
            if model_m_job:
                user_models.append(model_m_job)
    user_models = list(set(user_models))
    return user_models


def get_vip_job(username):
    running_vip = get_job_list(vip.DistributedJob, True)
    completed_vip = get_job_list(vip.DistributedJob, False) + running_vip
    vip_jobs = []
    for u_vip in completed_vip:
        # if u_vip.status.name in ('Waiting', 'Running'):
        #     print '---> ', u_vip.status.name, u_vip.id()
        if u_vip.username == username and u_vip.owner == True:
            vip_jobs.append(u_vip)
    return vip_jobs


def get_tuning_job(username):
    running_tuning = get_job_list(tuning.ParaJob, True)
    completed_tuning = get_job_list(tuning.ParaJob, False) + running_tuning
    tuning_jobs = []
    for u_tuning in completed_tuning:
        if u_tuning.username == username and u_tuning.owner == True:
            tuning_jobs.append(u_tuning)
    # print 'vip job 的列表', vip_jobs
    return tuning_jobs


@blueprint.route('/modelmanage',methods=['GET', 'POST'])
@requires_login
def modelmanage():
    username = flask.request.cookies.get('username')
    all_user_models = get_user_models(username,True)
    new_model_options = {
        'Images': {
            'image-classification': {
                'title': 'Classification',
                'url': flask.url_for(
                    'hyperai.model.images.classification.views.new'),
            },
            'image-other': {
                'title': 'Other',
                'url': flask.url_for(
                    'hyperai.model.images.generic.views.new'),
            },
        },
    }

    data_extensions = extensions.data.get_extensions()
    for extension in data_extensions:
        ext_category = extension.get_category()
        ext_title = extension.get_title()
        ext_id = extension.get_id()
        if ext_category not in new_model_options:
            new_model_options[ext_category] = {}
        new_model_options[ext_category][ext_id] = {
            'title': ext_id,
            'url': flask.url_for(
                'hyperai.model.images.generic.views.new',
                extension_id=ext_id),
        }
    user_models = []
    apply_scence = flask.request.args.get('apply_scence','none').lower()
    framework = flask.request.args.get('framework','none').lower()
    network = flask.request.args.get('network','none').lower()
    filter_list = []
    if network == 'other':
        network = 'custom'
    if apply_scence!='none':
        filter_list.append(apply_scence)
    if framework!='none':
        filter_list.append(framework)
    if network!='none':
        filter_list.append(network)
    if apply_scence == 'none' and framework == 'none' and network == 'none':
        user_models = all_user_models
    else:
        if apply_scence!='none' and framework!='none' and network!='none': # 三种筛选条件都不为none的情况下
            for model_s in all_user_models:
                # 同时满足三种条件
                if model_s.apply_scence in filter_list and model_s.train_task().get_framework_id() in filter_list and model_s.network in filter_list:
                   user_models.append(model_s)

        else:
            for model_s in all_user_models:
                if len(filter_list) == 2:
                    if (
                            model_s.apply_scence in filter_list and model_s.train_task().get_framework_id() in filter_list) or (
                            model_s.network in filter_list and model_s.apply_scence in filter_list) or (
                            model_s.train_task().get_framework_id() in filter_list and model_s.network in filter_list):
                        user_models.append(model_s)
                else:
                    if model_s.apply_scence in filter_list or model_s.train_task().get_framework_id() in filter_list or model_s.network in filter_list:
                        user_models.append(model_s)

    show_shouye_status = 0  # 显示首页状态
    name = flask.request.args.get('name', None)
    s_models = []
    if network == 'custom':
        network = 'other'
    if name:
        for s_model in user_models:
            if s_model.name() == name:
                s_models.append(s_model)
        user_models = s_models
    p = flask.request.args.get("p", '')  # 页数
    if p == '':
        p = 1
    else:
        p = int(p)
        if p > 1:
            show_shouye_status = 1
    length = len(user_models)
    for j in range(length - 1):
        for i in range(length - 1):
            if user_models[i].create_time_c < user_models[i + 1].create_time_c:
                user_models[i], user_models[i + 1] = user_models[i + 1], user_models[i]

    count = len(user_models)
    total = int(math.ceil(count / 6.0))  # 总页数

    dic = get_page(total, p)
    datas = {
        'p': int(p),
        'total': total,
        'show_shouye_status': show_shouye_status,
        'dic_list': dic,
        'user_models': user_models[(p - 1) * 6:p * 6],

    }
    return flask.render_template('/new/modelManage.html', index='model', datas=datas,
                                 new_model_options=new_model_options,apply_scence=apply_scence,framework=framework,network=network)


@blueprint.route('/modelmanage/detail/<job_id>')
@requires_login
def model_m_detail(job_id):
    job = scheduler.get_job(job_id)

    data_extensions = get_data_extensions()
    view_extensions = get_view_extensions()
    try:
        weight = job.dataset.image_dims[0]
        height = job.dataset.image_dims[1]
        job.size = str(weight) + 'X' + str(height)
    except Exception as e:
        job.size = None

        return flask.render_template('new/modelManagementDetails.html', job=job,data_extensions=data_extensions,
        view_extensions=view_extensions)
    return flask.render_template('new/modelManagementDetails.html', job=job)


@blueprint.route('/index', methods=['GET', 'POST'])
@requires_login
def index():
    threading.active_count()
    username = flask.request.cookies.get('username')
    if username == 'Administrator':
        all_jobs_p = scheduler.get_jobs()
        all_jobs_no_deployment = []
        user_models = []
        user_datasets = []
        other_job = []
        for job in all_jobs_p:
            if job.job_type != 'deployment_job':
                all_jobs_no_deployment.append(job)

        for job in all_jobs_no_deployment:
            if 'Dataset' in job.job_type():
                user_datasets.append(job)
            elif 'Model' in job.job_type():
                user_models.append(job)
            elif 'Job' in job.job_type():
                other_job.append(job)
        all_jobs = user_models + user_datasets + other_job
        all_user_models = user_models + other_job
    else:
        user_datasets = get_user_datasets(username,False)
        user_models = get_user_models(username,False)
        vip_jobs = get_vip_job(username)
        tuning_jobs = get_tuning_job(username)

        all_jobs = user_datasets + user_models + vip_jobs + tuning_jobs
        all_user_models = user_models + vip_jobs + tuning_jobs
    apply_scences = [a_model.apply_scence.encode('utf-8') if a_model.apply_scence else 'other' for a_model in
                     user_models]
    apply_d = Counter(apply_scences).most_common(6)
    backend = [b_dataset.apply_scence.encode('utf-8') for b_dataset in user_datasets]
    backend_d = Counter(backend).most_common(6)


    framework = [f_model.train_task().get_framework_id().encode('utf-8') for f_model in all_user_models]
    framework_d = Counter(framework).most_common(6)
    status = [s_job.status.name for s_job in all_jobs]
    status_d = Counter(status).most_common(5)
    sum_graph = [[list(a) for a in apply_d], [list(b) for b in backend_d], [list(f) for f in framework_d],
                 [list(s) for s in status_d]]
    data_begin = flask.request.args.get('data_begin', '')
    data_end = flask.request.args.get('data_end', '')

    if data_begin and data_end:
        data_begin = int(data_begin.replace('-',''))
        data_end = int(data_end.replace('-', ''))
    name = flask.request.args.get('name', '')
    run = flask.request.args.get('run', 'false')
    stop = flask.request.args.get('stop', 'false')
    error = flask.request.args.get('error', 'false')
    done = flask.request.args.get('done', 'false')
    wait = flask.request.args.get('wait','false')

    show_jobs = []
    filter_list = []
    # 在没有筛选条件的时候 默认显示所有
    if name == '' and run=='false' and stop=='false' and error=='false' and done== 'false' and wait== 'false' and data_begin =='' and data_end =='':

       show_jobs = all_jobs
    else:
        if run == 'true':
            filter_list.append('Running')
        if stop == 'true':
            filter_list.append('Aborted')
        if error == 'true':
            filter_list.append('Error')
        if done == 'true':
            filter_list.append('Done')
        if wait == 'true':
            filter_list.append('Waiting')
        if data_begin and data_end: # 在时间存在的情况下 遍历列表
            for job in all_jobs:
                if int(data_begin) <= int(job.create_time.split(' ')[0].replace('-', '')) <= int(data_end): # 查询这段时间内的所有job 然后再根据条件查询
                    # 既勾选了状态 又输入了名字
                    if name:
                        pattern = '.*'.join(name)  # Converts 'djm' to 'd.*j.*m'
                        regex = re.compile(pattern)  #
                        match = regex.search(job.name())
                        if job.status.name in filter_list and match:
                            show_jobs.append(job)
                        elif match and len(filter_list) == 0:
                            show_jobs.append(job)
                    # 在只勾选了状态 或者 只勾选了名字 情况下
                    elif len(filter_list)>0:
                        if job.status.name in filter_list:
                            show_jobs.append(job)
                    else:
                        show_jobs.append(job)
        else:
            for job in all_jobs:
                # 既勾选了状态 又输入了名字
                if name:
                    pattern = '.*'.join(name)  # Converts 'djm' to 'd.*j.*m'
                    regex = re.compile(pattern)  #
                    match = regex.search(job.name())
                    if job.status.name in filter_list and match:
                        show_jobs.append(job)
                    elif match and len(filter_list) == 0:
                        show_jobs.append(job)
                else:
                    if job.status.name in filter_list:
                        show_jobs.append(job)


    length = len(show_jobs)
    for j in range(length - 1):
        for i in range(length -1):
            if show_jobs[i].create_time_c < show_jobs[i+1].create_time_c:
                show_jobs[i],show_jobs[i+1] = show_jobs[i+1],show_jobs[i]

    show_shouye_status = 0  # 显示首页状态
    p = flask.request.args.get("p", '')  # 页数
    if p == '':
        p = 1
    else:
        p = int(p)
        if p > 1:
            show_shouye_status = 1
    count = len(show_jobs)

    total = int(math.ceil(count / 30.0))  # 总页数
    dic = get_page(total, p)

    datas = {
        'p': int(p),
        'total': total,
        'show_shouye_status': show_shouye_status,
        'dic_list': dic,
        'all_jobs': show_jobs[(p - 1) * 30:p * 30],

    }
    if username == 'Administrator':
        return flask.render_template('new/index_admin.html', index='index', sum_graph=sum_graph, datas=datas,name=name,run=run,stop=stop,error=error,done=done,wait=wait,data_begin=data_begin,data_end=data_end)
    else:
        return flask.render_template('new/index.html', index='index', sum_graph=sum_graph, datas=datas, name=name,
                                     run=run, stop=stop, error=error, wait=wait, done=done, data_begin=data_begin,
                                     data_end=data_end)


def fuzzyfinder(user_input, collection):
    suggestions = []
    pattern = '.*'.join(user_input)  # Converts 'djm' to 'd.*j.*m'
    regex = re.compile(pattern)  # Compiles a regex.
    for item in collection:
        match = regex.search(item)  # Checks if the current item matches the regex.
        if match:
            suggestions.append(item)
    return suggestions



def get_page(total,p):
    show_page = 5   # 显示的页码数
    pageoffset = 2  # 偏移量
    start = 1    #分页条开始
    end = total  #分页条结束

    if total > show_page:
        if p > pageoffset:
            start = p - pageoffset
            if total > p + pageoffset:
                end = p + pageoffset
            else:
                end = total
        else:
            start = 1
            if total > show_page:
                end = show_page
            else:
                end = total
        if p + pageoffset > total:
            start = start - (p + pageoffset - end)
    #用于模版中循环
    dic = range(start, end + 1)
    return dic


def json_dict(job, model_output_fields):
    d = {
        'id': job.id(),
        'name': job.name(),
        'group': job.group,
        'status': job.status_of_tasks().name,
        'status_css': job.status_of_tasks().css,
        'submitted': job.status_history[0][1],
        'elapsed': job.runtime_of_tasks(),
    }

    if 'train_db_task' in dir(job):
        d.update({
            'backend': job.train_db_task().backend,
        })

    if 'train_task' in dir(job):
        d.update({
            'framework': job.train_task().get_framework_id(),
        })

        for prefix, outputs in (('train', job.train_task().train_outputs),
                                ('val', job.train_task().val_outputs)):
            for key in outputs.keys():
                data = outputs[key].data
                if len(data) > 0:
                    key = '%s (%s) ' % (key, prefix)
                    model_output_fields.add(key + 'last')
                    model_output_fields.add(key + 'min')
                    model_output_fields.add(key + 'max')
                    d.update({key + 'last': data[-1]})
                    d.update({key + 'min': min(data)})
                    d.update({key + 'max': max(data)})

        if (job.train_task().combined_graph_data() and
                    'columns' in job.train_task().combined_graph_data()):
            d.update({
                'sparkline': job.train_task().combined_graph_data()['columns'][0][1:],
            })

    if 'get_progress' in dir(job):
        d.update({
            'progress': int(round(100 * job.get_progress())),
        })

    if hasattr(job, 'dataset_id'):
        d.update({
            'dataset_id': job.dataset_id,
        })

    if hasattr(job, 'extension_id'):
        d.update({
            'extension': job.extension_id,
        })
    else:
        if hasattr(job, 'dataset_id'):
            ds = scheduler.get_job(job.dataset_id)
            if ds and hasattr(ds, 'extension_id'):
                d.update({
                    'extension': ds.extension_id,
                })

    if isinstance(job, dataset.DatasetJob):
        d.update({'type': 'dataset'})

    if isinstance(job, model.ModelJob):
        d.update({'type': 'model'})

    if isinstance(job, pretrained_model.PretrainedModelJob):
        model_output_fields.add("has_labels")
        model_output_fields.add("username")
        d.update({
            'type': 'pretrained_model',
            'framework': job.framework,
            'username': job.username,
            'has_labels': job.has_labels_file()
        })
    return d


@blueprint.route('/completed_jobs.json', methods=['GET'])
@requires_login
def completed_jobs():
    """
    Returns JSON
        {
            datasets: [{id, name, group, status, status_css, submitted, elapsed, badge}],
            models:   [{id, name, group, status, status_css, submitted, elapsed, badge}],
        }
    """
    completed_datasets = get_job_list(dataset.DatasetJob, False)
    completed_models = get_job_list(model.ModelJob, False)
    running_datasets = get_job_list(dataset.DatasetJob, True)
    running_models = get_job_list(model.ModelJob, True)
    pretrained_models = get_job_list(pretrained_model.PretrainedModelJob, False)

    model_output_fields = set()
    data = {
        'running': [json_dict(j, model_output_fields) for j in running_datasets + running_models],
        'datasets': [json_dict(j, model_output_fields) for j in completed_datasets],
        'models': [json_dict(j, model_output_fields) for j in completed_models],
        'pretrained_models': [json_dict(j, model_output_fields) for j in pretrained_models],
        'model_output_fields': sorted(list(model_output_fields)),
    }

    return flask.jsonify(data)


@blueprint.route('/jobs/<job_id>/table_data.json', methods=['GET'])
@requires_login
def job_table_data(job_id):
    """
    Get the job data for the front page tables
    """
    job = scheduler.get_job(job_id)
    if job is None:
        raise werkzeug.exceptions.NotFound('Job not found')

    model_output_fields = set()
    return flask.jsonify({'job': json_dict(job, model_output_fields)})


def get_job_list(cls, running):
    return sorted(
        [j for j in scheduler.get_jobs() if isinstance(j, cls) and j.status.is_running() == running],
        key=lambda j: j.status_history[0][1],
        reverse=True,
    )


@blueprint.route('/group', methods=['GET', 'POST'])
@requires_login
def group():
    """
    Assign the group for the listed jobs
    """
    not_found = 0
    forbidden = 0
    group_name = utils.routing.get_request_arg('group_name').strip()
    job_ids = flask.request.form.getlist('job_ids[]')
    error = []
    for job_id in job_ids:
        try:
            job = scheduler.get_job(job_id)
            if job is None:
                logger.warning('Job %s not found for group assignment.' % job_id)
                not_found += 1
                continue

            if not utils.auth.has_permission(job, 'edit'):
                logger.warning('Group assignment not permitted for job %s' % job_id)
                forbidden += 1
                continue

            job.group = group_name

            # update form data so updated name gets used when cloning job
            if hasattr(job, 'form_data'):
                job.form_data['form.group_name.data'] = job.group

            job.emit_attribute_changed('group', job.group)

        except Exception as e:
            error.append(e)
            pass

    for job_id in job_ids:
        job = scheduler.get_job(job_id)

    error = []
    if not_found:
        error.append('%d job%s not found.' % (not_found, '' if not_found == 1 else 's'))

    if forbidden:
        error.append('%d job%s not permitted to be regrouped.' % (forbidden, '' if forbidden == 1 else 's'))

    if len(error) > 0:
        error = ' '.join(error)
        raise werkzeug.exceptions.BadRequest(error)

    return 'Jobs regrouped.'


@blueprint.route('/logout', methods=['GET', 'POST'])
@requires_login
def logout():
    """
    Unset the username cookie
    """
    next_url = utils.routing.get_request_arg('next') or \
               flask.request.referrer or flask.url_for('.home')

    response = flask.make_response(flask.redirect(next_url))
    response.set_cookie('username', '', expires=0)
    return response


# Jobs routes

@blueprint.route('/jobs/<job_id>', methods=['GET'])
@requires_login
def show_job(job_id):
    """
    Redirects to the appropriate /datasets/ or /models/ page
    """
    job = scheduler.get_job(job_id)
    if job is None:
        raise werkzeug.exceptions.NotFound('Job not found')

    if isinstance(job, dataset.DatasetJob):
        return flask.redirect(flask.url_for('hyperai.dataset.views.show', job_id=job_id))
    if isinstance(job, model.ModelJob):
        return flask.redirect(flask.url_for('hyperai.model.views.show', job_id=job_id))
    if isinstance(job, pretrained_model.PretrainedModelJob):
        return flask.redirect(flask.url_for('hyperai.pretrained_model.views.show', job_id=job_id))
    else:
        raise werkzeug.exceptions.BadRequest('Invalid job type')


@blueprint.route('/jobs/<job_id>', methods=['PUT'])
@requires_login
# @utils.auth.requires_login(redirect=False)
def edit_job(job_id):
    """
    Edit a job's name and/or notes
    """
    job = scheduler.get_job(job_id)
    if job is None:
        raise werkzeug.exceptions.NotFound('Job not found')

    if not utils.auth.has_permission(job, 'edit'):
        raise werkzeug.exceptions.Forbidden()

    # Edit name
    if 'job_name' in flask.request.form:
        name = flask.request.form['job_name'].strip()
        if not name:
            raise werkzeug.exceptions.BadRequest('name cannot be blank')
        job._name = name
        job.emit_attribute_changed('name', job.name())
        # update form data so updated name gets used when cloning job
        if 'form.dataset_name.data' in job.form_data:
            job.form_data['form.dataset_name.data'] = name
        elif 'form.model_name.data' in job.form_data:
            job.form_data['form.model_name.data'] = name
        else:
            # we are utterly confused
            raise werkzeug.exceptions.BadRequest('Unable to edit job type %s' % job.job_type())
        logger.info('Set name to "%s".' % job.name(), job_id=job.id())

    # Edit notes
    if 'job_notes' in flask.request.form:
        notes = flask.request.form['job_notes'].strip()
        if not notes:
            notes = None
        job._notes = notes
        logger.info('Updated notes.', job_id=job.id())

    return '%s updated.' % job.job_type()


@blueprint.route('/datasets/<job_id>/status', methods=['GET'])
@blueprint.route('/models/<job_id>/status', methods=['GET'])
@blueprint.route('/vip/<job_id>/status', methods=['GET'])
@blueprint.route('/jobs/<job_id>/status', methods=['GET'])
@blueprint.route('/tuning/<job_id>/status', methods=['GET'])
@requires_login
def job_status(job_id):
    """
    Returns a JSON objecting representing the status of a job
    """
    job = scheduler.get_job(job_id)
    result = {}
    if job is None:
        result['error'] = 'Job not found.'
    else:
        result['error'] = None
        result['status'] = job.status.name
        result['name'] = job.name()
        result['type'] = job.job_type()
    return json.dumps(result)


@blueprint.route('/delete_select_job', methods=['POST'])
@requires_login
def delete_select_job():
    job_ids = request.form.getlist('job_all[]')
    username = flask.request.cookies.get('username')
    user = User.query.filter_by(name=username).first()
    path = os.path.join(config_value("jobs_dir"), username, "jobs")
    # >>>   add at 2018-7-6   >>>
    forbidden_del_jobs = []
    failed_jobs = []
    # <<<   2018-7-6   <<<
    for job_id in job_ids:
        flag = delete_job_list(job_id, user, path)
        if flag == "true":
            pass
        elif flag == 3:
            msg = "Forbidden DEL. You can try to abort it first."
            forbidden_del_jobs.append({'res': 3, 'job_id': job_id, 'err': msg})
        else:
            failed_jobs.append({'res': 2, 'job_id': job_id, 'err': str(flag)})
    if len(forbidden_del_jobs) > 0 or len(failed_jobs) > 0:
        return flask.jsonify(
            {'res': 4, 'err': [len(forbidden_del_jobs), len(failed_jobs)]})
    # <<<   2018-7-6   <<<
    return flask.jsonify({'res': 1, 'info': 'job deleted'})


def delete_job_list(job_id, user, path):
    """
    Deletes a job
    """
    job = scheduler.get_job(job_id)
    # >>>   add at 2018-7-6   >>>
    if user.name == 'Administrator':
        job_path = os.path.join(config_value("jobs_dir"),job.username, "jobs")
    else:
        job_path = path
    from .status import Status
    if job.status in (Status.RUN, Status.WAIT, Status.INIT):
        return 3
    # <<<   2018-7-6   <<<

    if job is None:
        raise werkzeug.exceptions.NotFound('Job not found')

    # username = flask.request.cookies.get('username')
    # user = User.query.filter_by(name=username).first()
    # path = os.path.join(config_value("jobs_dir"), username, "jobs")
    if job.delete == True:
        try:
            if scheduler.delete_job(job_id):
                shutil.rmtree(os.path.join(job_path, job_id))
                # return flask.jsonify({'res': 1, 'info': 'job deleted'})
                return "true"
            else:
                raise werkzeug.exceptions.Forbidden('Job not deleted')
        except utils.errors.DeleteError as e:
            # return flask.jsonify({'res': 2, 'err': str(e)})
            return e
            # raise werkzeug.exceptions.Forbidden(str(e))
        except Exception as e:
            # print "---> ", e
            return 'true'
    elif job.delete == False:
        job.owner = False
        try:
            if job.dataset:
                model = Model.query.filter_by(job_id=job_id).first()
                user.models.remove(model)
                db.session.commit()
                # return flask.jsonify({'res': 'job deleted'})
                return "true"
        except Exception as e:
            dataset = Dataset.query.filter_by(job_id=job_id).first()
            user.datasets.remove(dataset)
            db.session.commit()
            # return flask.jsonify({'res': 'job deleted'})
            return "true"

@blueprint.route('/pretrained_models/<job_id>', methods=['DELETE'])
@blueprint.route('/datasets/<job_id>', methods=['DELETE'])
@blueprint.route('/models/<job_id>', methods=['DELETE'])
@blueprint.route('/vip/<job_id>', methods=['DELETE'])
@blueprint.route('/jobs/<job_id>', methods=['DELETE'])
@blueprint.route('/tuning/<job_id>', methods=['DELETE'])
@requires_login
def delete_job(job_id):
    """
    Deletes a job
    """
    job = scheduler.get_job(job_id)

    if job is None:
        raise werkzeug.exceptions.NotFound('Job not found')

    username = flask.request.cookies.get('username')
    user = User.query.filter_by(name=username).first()
    path = os.path.join(config_value("jobs_dir"), username, "jobs")
    if job.delete == True:
        try:
            if scheduler.delete_job(job_id):
                shutil.rmtree(os.path.join(path, job_id))
                return flask.jsonify({'res': 1, 'info': 'job deleted'})
            else:
                raise werkzeug.exceptions.Forbidden('Job not deleted')
        except utils.errors.DeleteError as e:
            return flask.jsonify({'res': 2, 'err': str(e)})
            # raise werkzeug.exceptions.Forbidden(str(e))
    elif job.delete == False:
        job.owner = False
        try:
            if job.dataset:
                model = Model.query.filter_by(job_id=job_id).first()
                user.models.remove(model)
                db.session.commit()
                return flask.jsonify({'res': 'job deleted'})
        except Exception as e:
            dataset = Dataset.query.filter_by(job_id=job_id).first()
            user.datasets.remove(dataset)
            db.session.commit()
            return flask.jsonify({'res': 'job deleted'})


@blueprint.route('/jobs', methods=['DELETE'])
@requires_login
def delete_jobs():
    """
    Deletes a list of jobs
    """
    not_found = 0
    forbidden = 0
    failed = 0
    job_ids = flask.request.form.getlist('job_ids[]')
    error = []
    for job_id in job_ids:

        try:
            job = scheduler.get_job(job_id)
            if job is None:
                not_found += 1
                continue

            if not utils.auth.has_permission(job, 'delete'):
                forbidden += 1
                continue

            if not scheduler.delete_job(job_id):
                failed += 1
                continue
        except Exception as e:
            error.append(str(e))
            pass

    if not_found:
        error.append('%d job%s not found.' % (not_found, '' if not_found == 1 else 's'))

    if forbidden:
        error.append('%d job%s not permitted to be deleted.' % (forbidden, '' if forbidden == 1 else 's'))

    if failed:
        error.append('%d job%s failed to delete.' % (failed, '' if failed == 1 else 's'))

    if len(error) > 0:
        error = ' '.join(error)
        raise werkzeug.exceptions.BadRequest(error)

    return 'Jobs deleted.'


@blueprint.route('/abort_jobs', methods=['POST'])
@requires_login
def abort_jobs():
    """
    Aborts a list of jobs
    """
    not_found = 0
    forbidden = 0
    failed = 0
    errors = []
    job_ids = flask.request.form.getlist('job_ids[]')
    for job_id in job_ids:

        try:
            job = scheduler.get_job(job_id)
            if job is None:
                not_found += 1
                continue

            if not utils.auth.has_permission(job, 'abort'):
                forbidden += 1
                continue

            if not scheduler.abort_job(job_id):
                failed += 1
                continue

        except Exception as e:
            errors.append(e)
            pass

    if not_found:
        errors.append('%d job%s not found.' % (not_found, '' if not_found == 1 else 's'))

    if forbidden:
        errors.append('%d job%s not permitted to be aborted.' % (forbidden, '' if forbidden == 1 else 's'))

    if failed:
        errors.append('%d job%s failed to abort.' % (failed, '' if failed == 1 else 's'))

    if len(errors) > 0:
        raise werkzeug.exceptions.BadRequest(' '.join(errors))

    return 'Jobs aborted.'


@blueprint.route('/abort/<job_id>',methods=['GET','POST'])
@requires_login
# @blueprint.route('/datasets/<job_id>/abort', methods=['POST'])
# @blueprint.route('/models/<job_id>/abort', methods=['POST'])
# @blueprint.route('/jobs/<job_id>/abort', methods=['POST'])
# @utils.auth.requires_login(redirect=False)
def abort_job(job_id):
    """
    Aborts a running job
    """
    job = scheduler.get_job(job_id)
    if job is None:
        raise werkzeug.exceptions.NotFound('Job not found')

    # print "views-abort_job: scheduler.abort_job({})".format(job_id)
    if scheduler.abort_job(job_id):
        return flask.redirect(flask.url_for('hyperai.views.index'))
    else:
        raise werkzeug.exceptions.Forbidden('Job not aborted')


@blueprint.route('/clone/<clone>', methods=['POST', 'GET'])
@requires_login
def clone_job(clone):
    """
    Clones a job with the id <clone>, populating the creation page with data saved in <clone>
    """

    # <clone> is the job_id to clone

    job = scheduler.get_job(clone)
    if job is None:
        raise werkzeug.exceptions.NotFound('Job not found')

    if isinstance(job, dataset.GenericDatasetJob):
        return flask.redirect(
            flask.url_for('hyperai.dataset.generic.views.new', extension_id=job.extension_id) + '?clone=' + clone)
    if isinstance(job, dataset.ImageClassificationDatasetJob):
        return flask.redirect(flask.url_for('hyperai.dataset.images.classification.views.new') + '?clone=' + clone)
    if isinstance(job, dataset.GenericImageDatasetJob):
        return flask.redirect(flask.url_for('hyperai.dataset.images.generic.views.new') + '?clone=' + clone)
    if isinstance(job, model.ImageClassificationModelJob):
        return flask.redirect(flask.url_for('hyperai.model.images.classification.views.new') + '?clone=' + clone)
    if isinstance(job, model.GenericImageModelJob):
        return flask.redirect(flask.url_for('hyperai.model.images.generic.views.new',extension_id=job.apply_scence if job.apply_scence != 'other' else None) + '?clone=' + clone)
    if isinstance(job, vip.DistributedJob):
        return flask.redirect(flask.url_for('hyperai.vip.views.new') + '?clone=' + clone)
    if isinstance(job, tuning.ParaJob):
        return flask.redirect(flask.url_for('hyperai.tuning.views.new') + '?clone=' + clone)
    else:
        raise werkzeug.exceptions.BadRequest('Invalid job type')


@app.errorhandler(Exception)
def handle_error(e):
    """
    Handle errors, formatting them as JSON if requested
    """
    error_type = type(e).__name__
    message = str(e)
    trace = None
    description = None
    status_code = 500
    if isinstance(e, werkzeug.exceptions.HTTPException):
        status_code = e.code
        description = e.description
    if app.debug:
        trace = traceback.format_exc().decode("utf-8")

    if request_wants_json():
        details = {
            'message': message,
            'type': error_type,
        }
        if description is not None:
            details['description'] = description
        if trace is not None:
            details['trace'] = trace.split('\n')
        return flask.jsonify({'error': details}), status_code
    else:
        message = message.replace('\\n', '<br />')
        if isinstance(e, hyperai.frameworks.errors.NetworkVisualizationError):
            trace = message
            message = ''
        return flask.render_template('error.html',
                                     title=error_type,
                                     message=message,
                                     description=description,
                                     trace=trace,
                                     ), status_code


# Register this handler for all error codes
# Necessary for flask<=0.10.1
for code in HTTP_STATUS_CODES:
    if code not in [301]:
        app.register_error_handler(code, handle_error)


# File serving


@blueprint.route('/files/<path:path>', methods=['GET'])
@requires_login
def serve_file(path):
    """
    Return a file in the jobs directory

    If you install the nginx.site file, nginx will serve files instead
    and this path will never be used
    """
    jobs_dir = config_value('jobs_dir')
    return flask.send_from_directory(jobs_dir, path)


import pwd
import stat


def is_readable(path, user):
    user_info = pwd.getpwnam(user)
    uid = user_info.pw_uid # 1001
    gid = user_info.pw_gid # 1001
    s = os.stat(path)
    mode = s[stat.ST_MODE]
    return (
        ((s[stat.ST_UID] == uid) and (mode & stat.S_IRUSR > 0)) or
        ((s[stat.ST_GID] == gid) and (mode & stat.S_IRGRP > 0)) or
        (mode & stat.S_IROTH > 0)

    )


@blueprint.route('/autocomplete/path', methods=['GET'])
@requires_login
def path_autocomplete():
    """
    Return a list of paths matching the specified preamble

    """
    name = flask.request.cookies.get('username')
    path = flask.request.args.get('query', '')
    # if not os.path.exists('/home/'+name):
    #     return flask.jsonify('无用户文件夹 请联系管理员')
    if path == '':
        path = os.path.join(config_value('jobs_dir'),name)

    if not os.path.isabs(path):
        # Only allow absolute paths by prepending forward slash
        path = os.path.sep + path
    if path == config_value('jobs_dir')+'/'+name:
        suggestions = [os.path.abspath(p) for p in glob.glob(path)]
    else:
        suggestions = [os.path.abspath(p) for p in glob.glob(path+'*')]
    if platform.system() == 'Windows':
        # on windows, convert backslashes with forward slashes
        suggestions = [p.replace('\\', '/') for p in suggestions]

    result = {
        "suggestions": sorted(suggestions)
    }
    # if is_readable(path,name):
    return json.dumps(result)
    # else:
    #     return flask.jsonify({'res':'user_error'})


@blueprint.route('/extension-static/<extension_type>/<extension_id>/<path:filename>')
@requires_login
def extension_static(extension_type, extension_id, filename):
    """
    Returns static files from an extension's static directory.
    '/extension-static/view/image-segmentation/js/app.js'
    would send the file
    'hyperai/extensions/view/imageSegmentation/static/js/app.js'
    """

    extension = None
    if (extension_type == 'view'):
        extension = extensions.view.get_extension(extension_id)
    elif (extension_type == 'data'):
        extension = extensions.data.get_extension(extension_id)

    if extension is None:
        raise ValueError("Unknown extension '%s'" % extension_id)

    hyperai_root = os.path.dirname(os.path.abspath(hyperai.__file__))
    rootdir = os.path.join(hyperai_root, *['extensions', 'view', extension.get_dirname(), 'static'])
    return flask.send_from_directory(rootdir, filename)


# SocketIO functions
# /home
@socketio.on('connect', namespace='/home')
def on_connect_home():
    """
    Somebody connected to the homepage
    """
    pass


@socketio.on('disconnect', namespace='/home')
def on_disconnect_home():
    """
    Somebody disconnected from the homepage
    """
    pass


# /jobs


@socketio.on('connect', namespace='/jobs')
def on_connect_jobs():
    """
    Somebody connected to a jobs page
    """
    pass


@socketio.on('disconnect', namespace='/jobs')
def on_disconnect_jobs():
    """
    Somebody disconnected from a jobs page
    """
    pass


@socketio.on('join', namespace='/jobs')
def on_join_jobs(data):
    """
    Somebody joined a room
    """
    room = data['room']
    join_room(room)
    flask.session['room'] = room


@socketio.on('leave', namespace='/jobs')
def on_leave_jobs():
    """
    Somebody left a room
    """
    if 'room' in flask.session:
        room = flask.session['room']
        del flask.session['room']
        leave_room(room)


@blueprint.route('/log/<job_id>', methods=['GET','POST'])
@requires_login
def log_new(job_id):

    job = scheduler.get_job(job_id)
    if isinstance(job,dataset.DatasetJob):
        job.log = True
    elif isinstance(job,model.ModelJob):
        job.log = False
    elif isinstance(job, DistributedJob):
        job.log = 'dis'
    elif isinstance(job, ParaJob):
        job.log = 'para'
    return flask.render_template('/new/log.html', job=job)

@blueprint.route('/url_verify',methods=['POST'])
@requires_login
def url_verify():
    path = flask.request.form.get('url')
    if path:
        if os.path.exists(path):
            res = 1
        else:
            res = 0
    else:
        res = 0
    return flask.jsonify({'res':res})


# @blueprint.route('/get_gpu_number',methods=['GET'])
# @requires_login
# def get_gpu_number():
#     total_gpu_count = scheduler.resources['gpus'].get_gpu_max()
#     # print total_gpu_count
#     remaining_gpu_count = scheduler.resources['gpus'].remaining()
#     # print remaining_gpu_count
#     username = flask.request.cookies.get('username')
#     user = User.query.filter_by(name=username).first()
#     if user.release:
#         gpu_max = User.get_gpu_max(username)
#         print "sssss %s"%gpu_max
#         # if r.get("{}_gpu".format(username)) is not None:
#         #     gpu_used = r.get("{}_gpu".format(username))
#         #     gpu_use = int(gpu_max) - int(gpu_used)
#         # else:
#         #     gpu_used = gpu_max
#         #     gpu_use = int(gpu_max) - int(gpu_used)
#         r.set("{}_gpu".format(username), gpu_max)
#         gpu_used = r.get("{}_gpu".format(username))
#         gpu_use = int(gpu_max) - int(gpu_used)
#         gpu_max = 0
#         # gpu_used = 0
#     else:
#         gpu_max = User.get_gpu_max(username)
#     # print gpu_max
#         if r.get("{}_gpu".format(username)) is not None:
#             gpu_used = r.get("{}_gpu".format(username))
#             gpu_use = int(gpu_max) - int(gpu_used)
#         else:
#             gpu_used = 0
#             gpu_use = int(gpu_max) - int(gpu_used)
#     # print int(gpu_max) - int(gpu_used)
#     # data = {'user_gpu':'{}/{}'.format((int(gpu_max) - int(gpu_used)), int(gpu_total))}
#     data = {'total_gpu_count':total_gpu_count, 'remaining_gpu_count':remaining_gpu_count, 'gpu_max':gpu_max, 'gpu_used':gpu_use}
#     return flask.jsonify(data)


@blueprint.route('/get_gpu_number',methods=['GET'])
@requires_login
def get_gpu_number():
    total_gpu_count = scheduler.resources['gpus'].get_gpu_max()
    # print total_gpu_count
    remaining_gpu_count = scheduler.resources['gpus'].remaining(look_gpu=True)
    # print remaining_gpu_count
    username = flask.request.cookies.get('username')
    user = User.query.filter_by(name=username).first()
    if user.release:
        # gpu_max = User.get_gpu_max(username)
        gpu_max = 0
        gpu_use = 0
    else:
        gpu_max = User.get_gpu_max(username)
        gpu_use = gpu_max - register_user.get_used_resource_about_user(username)
    data = {'total_gpu_count':total_gpu_count, 'remaining_gpu_count':remaining_gpu_count, 'gpu_max':gpu_max, 'gpu_used':gpu_use}
    return flask.jsonify(data)





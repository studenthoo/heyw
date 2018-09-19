#!/usr/bin/python
# -*- coding: utf-8 -*-s
# Copyright (c) 2014-2017, NVIDIA CORPORATION.  All rights reserved.
from __future__ import absolute_import

import io
import os
import sys
import platform
import subprocess
import hyperai
import json
import gevent
import time
import tarfile
import zipfile
import threading
import flask
import shutil
import json
import werkzeug.exceptions
from hyperai.config import config_value

from .job import DistributedJob
from .forms import VipForm
from flask import redirect, url_for
from hyperai.vip.task.tensorflow_distributed import DistributedTrain, Tensorflow
from hyperai.vip.task.tensorflow_mpi import MpiDistributedTrain, MpiTensorflow
from hyperai.vip.task.native_tensorflow import NativeDistributedTrain, NativeTensorflow
from hyperai.vip.task.caffe import Caffe, CaffeTrain
from hyperai.vip.task.mxnet import Mxnet, MxnetTrain
from hyperai.utils.time_filters import print_time_diff
from hyperai.vip.task.caffe_mpi import CaffeMpi, CaffeTrainMpi
from hyperai.vip.task.torch import Torch, TorchTrain
from hyperai.vip.task.pytorch import Pytorch, PytorchTrain
from hyperai.vip.task.cntk import Cntk, CntkTrain
from hyperai.vip.task.keras import Keras, KerasTrain

from hyperai import utils
from hyperai.utils.forms import fill_form_if_cloned, save_form_to_job
from hyperai.webapp import scheduler
from hyperai.utils.routing import request_wants_json, job_from_request
from hyperai.vip.task import query_framework_images
from hyperai.models import User
from hyperai.ext import r
from hyperai.utils.auth import requires_login
from MySQLdb import *
from hyperai.users import register_user
from flask import request

blueprint = flask.Blueprint(__name__, __name__)


@blueprint.route('/new', methods=['GET'])
@requires_login
def new():
    """
        Returns a form for a new DistributedJob
    """
    form = VipForm()
    job_id = flask.request.args.get('clone')
    fill_form_if_cloned(form)
    job = ''
    if job_id:
        job = scheduler.get_job(job_id)
    node_label_dict = scheduler.resources['gpus'].get_usable_label_gpu()
    new_node_label_dict = sorted(node_label_dict.items())

    data = {'clone':'no','usable_label_gpu_count':new_node_label_dict, 'total_gpu_count':scheduler.resources['gpus'].get_gpu_max(), 'remaining_gpu_count':scheduler.resources['gpus'].remaining(), 'index': 'vip'}
    return flask.jsonify(data)


@blueprint.route('/check_res', methods=['GET'])
@requires_login
def check_resources():
    gpu_count = flask.request.args.get('gpu_count')
    cpu_count = flask.request.args.get('cpu_count')
    memory_count = flask.request.args.get('memory_count')
    node_count = flask.request.args.get('node_count')
    ismore = flask.request.args.get('ismore')
    username = flask.request.cookies.get('username')
    if ismore == "0":
        node_count = 1
    else:
        node_count = node_count

    # check the resources about user
    gpu_max = User.get_gpu_max(username)
    gpu_total = int(gpu_count) * int(node_count)
    # user = User.query.filter_by(name=username).first()

    res = register_user.is_enough_resource_about_user(username, gpu_total, gpu_max)
    if not res:
        num = register_user.get_used_resource_about_user(username)
        data = {'a': 0, 'res': '您的信息：可用GPU/申请GPU：{}/{}'.format((int(gpu_max) - num), int(gpu_total))}
        return flask.jsonify(data)
    elif res == 'Forbid':
        return flask.jsonify({'a': 0, 'res': '您已被管理员禁用，请尝试联系管理员'})
    else:
        return flask.jsonify({'a': 1})


@blueprint.route('/frame_select', methods=['GET', 'POST'])
@requires_login
def frame_select():
    """
        Returns a version list from frame
    """
    if flask.request.method == 'POST':
        job_id = flask.request.form.get('frame_obj')
        if job_id:
            job = scheduler.get_job(job_id)
        frame_list = query_framework_images.get_frame()
    return flask.jsonify(frame_list)


@blueprint.route('/get_framework', methods=['GET', 'POST'])
def get_framework():
    _conn_status = True
    _max_retries_count = 5
    _conn_retries_count = 0
    _conn_timeout = 5
    a = {}
    username = request.cookies.get('username')
    share_dict = {}
    private_dict={}
    value = []
    while _conn_status and _conn_retries_count <= _max_retries_count:
        try:
            conn = connect(host=config_value('img_mysql_ip'), port=config_value('img_mysql_port'),
                           user=config_value('img_mysql_user'), passwd=config_value('img_mysql_password'),
                           db=config_value('img_mysql_db'), charset='utf8', connect_timeout=_conn_timeout)
            _conn_status = False
            cursor1 = conn.cursor()
            share_sql = 'select distinct r.name,r.creation_time from repository as r join project_metadata as pm on(r.project_id = pm.project_id) join access_log as a on (r.name=a.repo_name) where pm.value = "'"true"'" and a.operation="'"push"'" and (SELECT TIMESTAMPDIFF(SECOND,r.creation_time,a.op_time)>=0)'
            cursor1.execute(share_sql)
            share_value = cursor1.fetchall()
            share_dict['share_value'] = share_value
            value.append(share_dict)
            private_sql = 'select distinct r.name,r.creation_time from repository as r join project_member as pr on (pr.project_id=r.project_id) join project_metadata as pm on (r.project_id=pm.project_id) join user as u on (u.user_id=pr.user_id) join access_log as a on (r.name=a.repo_name) where pm.value="'"false"'" and u.username="'"%s"'" and u.deleted=false and pm.deleted=false and a.operation="'"push"'" and (SELECT TIMESTAMPDIFF(SECOND,r.creation_time,a.op_time)>=0)' % username
            cursor1.execute(private_sql)
            private_value = cursor1.fetchall()
            private_dict['private_value'] = private_value
            value.append(private_dict)
            cursor1.close()
            conn.close()
            with open(os.path.join(config_value("public_dir"), 'image_new_version.txt'), 'w+') as w_file:
                w_file.write('%s' % value)
            w_file.close()
            a['statu'] = 'Successful!'
        except Exception as e:
            _conn_retries_count += 1
            a['statu'] = 'Can\'t connect to Mysql'
            print e
    return flask.jsonify(a)


@blueprint.route('/distributed_create', methods=['POST'])
@requires_login
def distributed_create():
    framework = request.form.get('framework')
    print "framework", framework
    framework_name = request.form.get('framework_name')
    print "frame_name", framework_name
    framework_tag = request.form.get('framework_tag')
    print "frame_tag", framework_tag
    # homework_name = form.homework_name.data
    homework_name = request.form.get('homework_name')
    print "homework", homework_name
    images_list = flask.request.files.getlist('image_list')
    print "image_list", images_list
    # extra_parameter = form.extra_parameter.data #额外参数
    extra_parameter = request.form.get("extra_parameter")
    print "extra_parameter", extra_parameter
    cpu_count = request.form.get("cpu_count")
    cpu_count = int(cpu_count)
    print "cpu_count", cpu_count
    # gpu_count = form.gpu_count.data
    gpu_count = request.form.get("gpu_count")
    print "gpu_count", gpu_count
    gpu_count = int(gpu_count)
    memory = request.form.get("memory")
    memory = int(memory)
    # memory = form.memory_count.data
    node_count = request.form.get("node_count")
    print "node_count",node_count
    # matchExpressions_values = form.node_label_choice.data
    matchExpressions_values = request.form.get("matchExpressions_values")
    print "matchExpressions_values", matchExpressions_values
    username = utils.auth.get_username()
    mount_path = config_value('jobs_dir')
    model_path = os.path.join(config_value('jobs_dir'), username + '/' + 'code' + '/')
    gpu_tatol = int(gpu_count) * int(node_count)
    # max_run_time = form.max_run_time.data
    max_run_time = request.form.get("max_run_time")
    print "max_run_time", max_run_time
    # server_path = form.server_path.data.encode('utf-8')#代码服务器路径
    server_path = request.form.get("server_path").encode('utf-8')
    print "server_path", server_path
    # caffe_path = form.caffe_path.data.encode('utf-8')#
    caffe_path = request.form.get("caffe_path").encode('utf-8')
    print "caffe_path", caffe_path
    # solver_path = form.solver_path.data.encode('utf-8')#
    solver_path = request.form.get("solver_path").encode('utf-8')
    print "solver_path", solver_path
    # main_name = form.main_name.data.encode('utf-8')#主文件路径
    main_name = request.form.get("main_name").encode('utf-8')
    print "main_name", main_name
    base_path = ''
    file_path = ''


    if server_path or solver_path:
        if os.path.isdir(server_path):
            if main_name:
                file_path = os.path.join(server_path, main_name)
                file_path_str = str(file_path)
        else:
            if solver_path:
                base_path = solver_path
                file_path_str = str(base_path)
                file_path = caffe_path
            else:
                file_path = server_path
                file_path_str = str(file_path)
    else:
        if images_list:
            for model_file in images_list:
                file_name = model_file.filename.encode('utf-8')
                print 'file_name', file_name
                if file_name == main_name:
                    base_path = model_path.encode('utf-8') + file_name
                    print "base_path", base_path
                    file_path_str = str(base_path)
                else:
                    file_path = model_path.encode('utf-8') + file_name
                    print "file_path", file_path
                    file_path_str = str(file_path)
                model_file.save(os.path.join(model_path, file_name))
    if framework == 'caffempi':
        if not base_path:
            raise ValueError('The main file name does not match the actual file')

    try:
        if file_path_str.endswith('.zip'):
            base_dir, file_name = os.path.split(file_path_str)
            unzip_file(file_path_str, base_dir)
            zip_prefix = str(file_name).replace('.zip', '')
            file_path = os.path.join(base_dir, zip_prefix, main_name)
        elif file_path_str.endswith('.tar.gz'):
            tar_file_dir = file_path_str.replace('.tar.gz', '')
            tar_file(file_path_str, tar_file_dir)
    except Exception as e:
        print e
        return flask.make_response('文件上传失败')

    if not file_path:
        raise ValueError('The file is not exist!')

    job = None
    if framework == 'caffempi':
        caffe_obj = CaffeMpi('caffempi', 'distributed')
        try:
            job = DistributedJob(username=utils.auth.get_username(),
                                 name=homework_name,
                                 mode='distributed',
                                 node_count=range(int(node_count) + 1),
                                 framework=framework,
                                 cpu_count=cpu_count,
                                 main_name=main_name,)

            def fun_timer():
                job.abort()

            if max_run_time:
                max_run_time_second = float(max_run_time) * 60
                timer = threading.Timer(max_run_time_second, fun_timer)
                timer.start()

            job.tasks.append(caffe_obj.create_train_task(job=job,
                                                         node_count=node_count,
                                                         file_path=file_path,
                                                         base_path=base_path,
                                                         cpu_count=cpu_count,
                                                         gpu_count=gpu_count,
                                                         memory=memory,
                                                         data_dir="",
                                                         train_dir="",
                                                         test_dir="",
                                                         framework=framework,
                                                         framework_version="",
                                                         framework_name=framework_name,
                                                         framework_tag=framework_tag,
                                                         model_dir=model_path,
                                                         mount_path=mount_path,
                                                         username=username,
                                                         extra_parameter=extra_parameter,
                                                         matchExpressions_values=matchExpressions_values,
                                                         ))

            # save_form_to_job(job, form)
            scheduler.add_job(job)
        except:
            if job:
                scheduler.delete_job(job)
            raise
        # return redirect(url_for('hyperai.vip.views.show', job_id=job.id()))
    elif framework == 'tensorflowmpi':
        mpitf_obj = MpiTensorflow('distributed_tensorflow', 'distributed')
        try:
            job = DistributedJob(username=utils.auth.get_username(),
                                 name=homework_name,
                                 mode='distributed',
                                 node_count=range(int(node_count)),
                                 framework=framework,
                                 cpu_count=cpu_count,
                                 main_name=main_name,)

            def fun_timer():
                job.abort()

            if max_run_time:
                max_run_time_second = float(max_run_time) * 60
                timer = threading.Timer(max_run_time_second, fun_timer)
                timer.start()

            job.tasks.append(mpitf_obj.create_train_task(
                job=job,
                node_count=node_count,
                file_path=file_path,
                cpu_count=cpu_count,
                gpu_count=gpu_count,
                memory=memory,
                data_dir="",
                framework=framework,
                framework_version="",
                framework_name=framework_name,
                framework_tag=framework_tag,
                mount_path=mount_path,
                username=username,
                extra_parameter=extra_parameter,
                matchExpressions_values=matchExpressions_values,
            ))

            # save_form_to_job(job, form)
            scheduler.add_job(job)
        except:
            if job:
                scheduler.delete_job(job)
            raise
        # return redirect(url_for('hyperai.vip.views.show', job_id=job.id()))
    elif framework == 'tensorflow':
        native_tf_obj = NativeTensorflow('distributed_tensorflow', 'distributed')
        try:
            job = DistributedJob(username=utils.auth.get_username(),
                                 name=homework_name,
                                 mode='distributed',
                                 node_count=range(int(node_count)),
                                 framework="tensorflow",
                                 cpu_count=cpu_count,
                                 main_name=main_name,)

            def fun_timer():
                job.abort()

            if max_run_time:
                max_run_time_second = float(max_run_time) * 60
                timer = threading.Timer(max_run_time_second, fun_timer)
                timer.start()

            job.tasks.append(native_tf_obj.create_train_task(
                job=job,
                node_count=node_count,
                file_path=file_path,
                cpu_count=cpu_count,
                gpu_count=gpu_count,
                memory=memory,
                data_dir="",
                framework=framework,
                framework_version="",
                framework_name=framework_name,
                framework_tag=framework_tag,
                mount_path=mount_path,
                username=username,
                extra_parameter=extra_parameter,
                matchExpressions_values=matchExpressions_values,
            ))

            # save_form_to_job(job, form)
            scheduler.add_job(job)
        except:
            if job:
                scheduler.delete_job(job)
            raise
    data = {'job_id': job.id(), 'statue': job.train_task().status.name, 'create_time': job.create_time,
            'job_username': job.username, 'runtime_of_tasks': print_time_diff(job.runtime_of_tasks()),
            'job_type': job.job_type(), 'job_framework': job.framework, 'job_name': job.name()}
    # 'job_name': job.name, , 'get_data': job.get_data(), 'log_data': job.log_data
    print data
    return flask.jsonify(data)
        # return redirect(url_for('hyperai.vip.views.show', job_id=job.id()))
    # else:
    #     pass


@blueprint.route('/log_file', methods=['GET', 'POST'])
@requires_login
def show_log():
    framework = flask.request.args.get('framework')
    job_id = flask.request.args.get('job_id')
    username = utils.auth.get_username()
    log_dir = os.path.join(config_value('jobs_dir'), username, 'jobs', str(job_id))

    log_name = "au_%s_output.log" % framework
    log_path = os.path.join(log_dir, log_name)
    if os.path.exists(log_path):
        with open(log_path, 'rt') as logs:
            logs = logs.readlines()
            return flask.render_template('/new/exe_log.html', logs=logs)
    else:
        return flask.make_response('The log is not exist!')


@blueprint.route('/single_create', methods=['POST'])
@requires_login
def single_create():
    framework = request.form.get('framework')
    print "framework",framework
    framework_name = request.form.get('framework_name')
    print "frame_name",framework_name
    framework_tag = request.form.get('framework_tag')
    print "frame_tag",framework_tag
    homework_name = request.form.get('homework_name')
    print "homework",homework_name
    images_list = flask.request.files.getlist('image_list')
    print "image_list",images_list
    extra_parameter = request.form.get("extra_parameter")
    print "extra_parameter",extra_parameter
    cpu_count = request.form.get("cpu_count")
    cpu_count = int(cpu_count)
    print "cpu_count",cpu_count
    gpu_count = request.form.get("gpu_count")
    print "gpu_count",gpu_count
    gpu_count = int(gpu_count)
    memory = request.form.get("memory")
    memory = int(memory)
    node_count = 1
    matchExpressions_values = request.form.get("matchExpressions_values")
    print "matchExpressions_values",matchExpressions_values
    username = utils.auth.get_username()
    mount_path = config_value('jobs_dir')
    model_path = os.path.join(config_value('jobs_dir'), username + '/' + 'code' + '/')
    gpu_tatol = int(gpu_count)
    max_run_time = request.form.get("max_run_time")
    print "max_run_time",max_run_time
    server_path = request.form.get("server_path").encode('utf-8')
    print "server_path", server_path
    caffe_path = request.form.get("caffe_path").encode('utf-8')
    print "caffe_path", caffe_path
    solver_path = request.form.get("solver_path").encode('utf-8')
    print "solver_path", solver_path
    main_name = request.form.get("main_name").encode('utf-8')
    print "main_name", main_name
    base_path = ''
    file_path = ''

    if server_path or solver_path:
        if os.path.isdir(server_path):
            if main_name:
                file_path = os.path.join(server_path, main_name)
                file_path_str = str(file_path)
        else:
            if solver_path:
                base_path = solver_path
                file_path_str = str(base_path)
                file_path = caffe_path
            else:
                file_path = server_path
                file_path_str = str(file_path)
    else:
        if images_list:
            for model_file in images_list:
                print "model_file",model_file.filename
                file_name = model_file.filename.encode('utf-8')
                if file_name == main_name:
                    base_path = model_path.encode('utf-8') + file_name
                    file_path_str = str(base_path)
                else:
                    file_path = model_path.encode('utf-8') + file_name
                    file_path_str = str(file_path)

                model_file.save(os.path.join(model_path, file_name))
    if framework == 'caffe':
        if not base_path:
            raise ValueError('The main file name does not match the actual file')
    try:
        if file_path_str.endswith('.zip'):
            base_dir, file_name = os.path.split(file_path_str)
            unzip_file(file_path_str, base_dir)
            zip_prefix = str(file_name).replace('.zip', '')
            file_path = os.path.join(base_dir, zip_prefix, main_name)
        elif file_path_str.endswith('.tar.gz'):
            tar_file_dir = file_path_str.replace('.tar.gz', '')
            tar_file(file_path_str, tar_file_dir)
        else:
            pass
    except Exception as e:
        print e
        return flask.make_response('文件上传失败')

    if not file_path:
        raise ValueError('The file is not exist!')
    if framework == "tensorflow":
        tf_obj = Tensorflow('tensorflow', 'single')
        job = DistributedJob(username=utils.auth.get_username(),
                             name=homework_name,
                             mode='single',
                             node_count=range(node_count),
                             framework=framework,
                             cpu_count=cpu_count,
                             main_name=main_name,
                             )

        def fun_timer():
            job.abort()

        if max_run_time:
            max_run_time_second = float(max_run_time) * 60
            timer = threading.Timer(max_run_time_second, fun_timer)
            timer.start()

        job.tasks.append(tf_obj.create_train_task(job=job,
                                                  node_count=node_count,
                                                  file_path=file_path,
                                                  cpu_count=cpu_count,
                                                  gpu_count=gpu_count,
                                                  memory=memory,
                                                  data_dir="",
                                                  framework=framework,
                                                  framework_version="",
                                                  framework_name=framework_name,
                                                  framework_tag=framework_tag,
                                                  mount_path=mount_path,
                                                  username=username,
                                                  extra_parameter=extra_parameter,
                                                  matchExpressions_values=matchExpressions_values,
                                                  ))
    elif framework == "caffe":
        caffe_obj = Caffe('caffe', 'single')
        job = DistributedJob(username=utils.auth.get_username(),
                             name=homework_name,
                             mode='single',
                             node_count=range(node_count),
                             framework=framework,
                             cpu_count=cpu_count,
                             main_name=main_name,)

        def fun_timer():
            job.abort()

        if max_run_time:
            max_run_time_second = float(max_run_time) * 60
            timer = threading.Timer(max_run_time_second, fun_timer)
            timer.start()

        job.tasks.append(caffe_obj.create_train_task(job=job,
                                                     node_count=node_count,
                                                     file_path=file_path,
                                                     base_path=base_path,
                                                     cpu_count=cpu_count,
                                                     gpu_count=gpu_count,
                                                     memory=memory,
                                                     data_dir="",
                                                     train_dir="",
                                                     test_dir="",
                                                     framework=framework,
                                                     framework_version="",
                                                     framework_name=framework_name,
                                                     framework_tag=framework_tag,
                                                     model_dir=model_path,
                                                     mount_path=mount_path,
                                                     username=username,
                                                     extra_parameter=extra_parameter,
                                                     matchExpressions_values=matchExpressions_values,
                                                     ))
    elif framework == "torch":
        torch_obj = Torch('torch', 'single')
        job = DistributedJob(username=utils.auth.get_username(),
                             name=homework_name,
                             mode='single',
                             node_count=range(node_count),
                             framework=framework,
                             cpu_count=cpu_count,
                             main_name=main_name,)

        def fun_timer():
            job.abort()

        if max_run_time:
            max_run_time_second = float(max_run_time) * 60
            timer = threading.Timer(max_run_time_second, fun_timer)
            timer.start()

        job.tasks.append(torch_obj.create_train_task(job=job,
                                                     node_count=node_count,
                                                     file_path=file_path,
                                                     cpu_count=cpu_count,
                                                     gpu_count=gpu_count,
                                                     memory=memory,
                                                     data_dir="",
                                                     framework=framework,
                                                     framework_version="",
                                                     framework_name=framework_name,
                                                     framework_tag=framework_tag,
                                                     model_dir=model_path,
                                                     mount_path=mount_path,
                                                     username=username,
                                                     extra_parameter=extra_parameter,
                                                     matchExpressions_values=matchExpressions_values,
                                                     ))
    elif framework == "pytorch":
        pytorch_obj = Pytorch('pytorch', 'single')
        job = DistributedJob(username=utils.auth.get_username(),
                             name=homework_name,
                             mode='single',
                             node_count=range(node_count),
                             framework=framework,
                             cpu_count=cpu_count,
                             main_name=main_name,)

        def fun_timer():
            job.abort()

        if max_run_time:
            max_run_time_second = float(max_run_time) * 60
            timer = threading.Timer(max_run_time_second, fun_timer)
            timer.start()

        job.tasks.append(pytorch_obj.create_train_task(job=job,
                                                       node_count=node_count,
                                                       file_path=file_path,
                                                       cpu_count=cpu_count,
                                                       gpu_count=gpu_count,
                                                       memory=memory,
                                                       data_dir="",
                                                       framework=framework,
                                                       framework_version="",
                                                       framework_name=framework_name,
                                                       framework_tag=framework_tag,
                                                       model_dir=model_path,
                                                       mount_path=mount_path,
                                                       username=username,
                                                       extra_parameter=extra_parameter,
                                                       matchExpressions_values=matchExpressions_values,
                                                       ))
    elif framework == 'mxnet':
        mxnet_obj = Mxnet('mxnet', 'single')
        job = DistributedJob(username=utils.auth.get_username(),
                             name=homework_name,
                             mode='single',
                             node_count=range(int(node_count) + 1),
                             framework=framework,
                             cpu_count=cpu_count,
                             main_name=main_name,)

        def fun_timer():
            job.abort()

        if max_run_time:
            max_run_time_second = float(max_run_time) * 60
            timer = threading.Timer(max_run_time_second, fun_timer)
            timer.start()

        job.tasks.append(mxnet_obj.create_train_task(
            job=job,
            node_count=node_count,
            file_path=file_path,
            cpu_count=cpu_count,
            gpu_count=gpu_count,
            memory=memory,
            data_dir="",
            framework=framework,
            framework_version="",
            framework_name=framework_name,
            framework_tag=framework_tag,
            mount_path=mount_path,
            username=username,
            extra_parameter=extra_parameter,
            matchExpressions_values=matchExpressions_values,
        ))
    elif framework == 'cntk':
        cntk_obj = Cntk('cntk', 'single')
        job = DistributedJob(username=utils.auth.get_username(),
                             name=homework_name,
                             mode='single',
                             node_count=range(int(node_count) + 1),
                             framework=framework,
                             cpu_count=cpu_count,
                             main_name=main_name,)

        def fun_timer():
            job.abort()
        if max_run_time:
            max_run_time_second = float(max_run_time) * 60
            timer = threading.Timer(max_run_time_second, fun_timer)
            timer.start()

        job.tasks.append(cntk_obj.create_train_task(
            job=job,
            node_count=node_count,
            file_path=file_path,
            cpu_count=cpu_count,
            gpu_count=gpu_count,
            memory=memory,
            data_dir='',
            framework=framework,
            # framework_version=frame_version,
            framework_name=framework_name,
            framework_tag=framework_tag,
            mount_path=mount_path,
            username=username,
            extra_parameter=extra_parameter,
            matchExpressions_values=matchExpressions_values,
        ))
    elif framework == 'keras':
        keras_obj = Keras('keras', 'single')
        job = DistributedJob(username=utils.auth.get_username(),
                             name=homework_name,
                             mode='single',
                             node_count=range(int(node_count) + 1),
                             framework=framework,
                             cpu_count=cpu_count,
                             main_name=main_name,)

        def fun_timer():
            job.abort()
        if max_run_time:
            max_run_time_second = float(max_run_time) * 60
            timer = threading.Timer(max_run_time_second, fun_timer)
            timer.start()

        job.tasks.append(keras_obj.create_train_task(
            job=job,
            node_count=node_count,
            file_path=file_path,
            cpu_count=cpu_count,
            gpu_count=gpu_count,
            memory=memory,
            data_dir='',
            framework=framework,
            framework_name=framework_name,
            framework_tag=framework_tag,
            mount_path=mount_path,
            username=username,
            extra_parameter=extra_parameter,
            matchExpressions_values=matchExpressions_values,
        ))
    else:
        pass
    scheduler.add_job(job)
    data = {'job_id':job.id(), 'statue': job.train_task().status.name, 'create_time': job.create_time,
             'job_username': job.username, 'runtime_of_tasks':print_time_diff(job.runtime_of_tasks()),
            'job_type':job.job_type(), 'job_framework': job.framework,'job_name': job.name()}
    print data
    return flask.jsonify(data)


def vip_show(job):
    return flask.render_template('/new/v-homeworkMonitor.html', job=job)


@blueprint.route('/<job_id>.json', methods=['GET'])
@blueprint.route('/<job_id>', methods=['GET'])
@requires_login
def show(job_id):
    job = scheduler.get_job(job_id)
    if job is None:
        raise werkzeug.exceptions.NotFound('Job not found')
    if isinstance(job, DistributedJob):
        return vip_show(job)


# 下载的日志的功能
@blueprint.route('/download/<job_id>', methods=['GET'])
@requires_login
def download_log(job_id):
    """
    Return a file in the jobs directory
    If you install the nginx.site file, nginx will serve files instead
    and this path will never be used
    """
    framework = flask.request.args.get('framework')
    # job_id = flask.request.args.get('job_id')
    try:
        job_id
    except Exception as e:
        raise ValueError("No job_id !")

    username = utils.auth.get_username()
    log_dir = os.path.join(config_value('jobs_dir'), username, 'jobs', str(job_id))
    mpi_log_name = "au_%s_output" % (framework)
    name = '{}.log'.format(mpi_log_name)

    return flask.send_from_directory(log_dir, name, as_attachment=True)


@blueprint.route('/get_data', methods=['GET','POST'])
@requires_login
def get_data():

    job_id = request.form.get('job_id')
    if job_id:
        job = scheduler.get_job(job_id)
        data = {'log_data':job.log_data(), 'graph_data':job.get_data(),'name':job.username, 'create_time': job.create_time,
                'runtime_of_tasks':print_time_diff(job.runtime_of_tasks()), 'job_name': job.name(), 'statue': job.train_task().status.name,
                'job_framework': job.framework }
        return flask.jsonify(data)
    else:
        pass


def unzip_file(zipfilename, unziptodir):
    """
    | ##@函数目的: 解压zip文件到指定目录
    | ##@参数说明：zipfilename为zip文件路径，unziptodir为解压文件后的文件目录
    | ##@返回值：无
    | ##@函数逻辑：
    """
    if not os.path.exists(unziptodir):
        # 创建目录 并设置权限
        os.mkdir(unziptodir, 0777)
    zfobj = zipfile.ZipFile(zipfilename)
    # print 'zfobj', zfobj
    for name in zfobj.namelist():
        name = name.replace('\\', '/')
        if name.endswith('/'):
            p = os.path.join(unziptodir, name[:-1])
            if os.path.exists(p):
                # 如果文件夹存在，就删除之：避免有新更新无法复制
                shutil.rmtree(p)
            os.mkdir(p)
        else:
            ext_filename = os.path.join(unziptodir, name)
            ext_dir = os.path.dirname(ext_filename)
            if not os.path.exists(ext_dir):
                os.mkdir(ext_dir, 0777)
            outfile = open(ext_filename, 'wb')
            outfile.write(zfobj.read(name))
            outfile.close()


def tar_file(tarfilename, untartodir):
    """
    | ##@函数目的: 解压zip文件到指定目录
    | ##@参数说明：zipfilename为zip文件路径，unziptodir为解压文件后的文件目录
    | ##@返回值：无
    | ##@函数逻辑：
    """
    if not os.path.exists(untartodir):
        os.mkdir(untartodir, 0777)
    tarobj = tarfile.TarFile(tarfilename)
    for name in tarobj.namelist():
        name = name.replace('\\', '/')

        if name.endswith('/'):
            p = os.path.join(untartodir, name[:-1])
            if os.path.exists(p):
                # 如果文件夹存在，就删除之：避免有新更新无法复制
                shutil.rmtree(p)
            os.mkdir(p)
        else:
            ext_filename = os.path.join(untartodir, name)

            ext_dir = os.path.dirname(ext_filename)
            if not os.path.exists(ext_dir):
                os.mkdir(ext_dir, 0777)
            outfile = open(ext_filename, 'wb')
            outfile.write(tarobj.read(name))
            outfile.close()


def get_framework_by_images():
    framework_list = [
        ('tensorflow', 'tensorflow'),
    ]
    if framework_list is not None:
        return framework_list
    else:
        return flask.make_response('没有框架！')


def get_frame_version_by_images():
    frame_version_list = [
        ('v1.2.0', 'v1.2.0'),
    ]
    if frame_version_list is not None:
        return frame_version_list
    else:
        return flask.make_response('没有框架版本！')




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
from hyperai.vip.task.caffe2 import Caffe2, DistributedCaffe2Train
from hyperai.vip.task.caffe import Caffe, CaffeTrain
from hyperai.vip.task.mxnet import Mxnet, MxnetTrain

from hyperai.vip.task.caffe_mpi import CaffeMpi, CaffeTrainMpi
from hyperai.vip.task.torch import Torch, TorchTrain
from hyperai.vip.task.pytorch import Pytorch, PytorchTrain
from hyperai import utils
from hyperai.utils.forms import fill_form_if_cloned, save_form_to_job
from hyperai.webapp import scheduler
from hyperai.utils.routing import request_wants_json, job_from_request
from hyperai.vip.task import query_framework_images
from hyperai.models import User
# from hyperai.ext import r
from hyperai.utils.auth import requires_login
from MySQLdb import *
from hyperai.users import register_user

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
    label_gpu_value = [v for k, v in sorted(node_label_dict.items())]
    return flask.render_template('new/Vipuser.html',
                                 form=form,
                                 job=job,
                                 total_gpu_count=scheduler.resources['gpus'].get_gpu_max(),
                                 remaining_gpu_count=scheduler.resources['gpus'].remaining(),
                                 index='vip',
                                 usable_label_gpu_count=label_gpu_value,
                                 )


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
    while _conn_status and _conn_retries_count <= _max_retries_count:
        try:
            conn = connect(host=config_value('img_mysql_ip'), port=config_value('img_mysql_port'), user=config_value('img_mysql_user'), passwd=config_value('img_mysql_password'), db=config_value('img_mysql_db'), charset='utf8', connect_timeout=_conn_timeout)
            _conn_status = False
            cursor1 = conn.cursor()
            sql = 'select name from repository order by repository_id'
            cursor1.execute(sql)
            value = cursor1.fetchall()
            cursor1.close()
            conn.close()
            with open(os.path.join(config_value("public_dir"), 'image_version.txt'), 'w+') as w_file:
                for image in value:
                    for line in image:
                        w_file.write('%s\n' % line)
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
    form = VipForm()
    fill_form_if_cloned(form)
    framework = form.framework.data
    frame_version = form.frame_version.data
    homework_name = form.homework_name.data
    images_list = flask.request.files.getlist('image_list')
    dataset_path = form.data_path.data.encode('utf-8')
    train_path = form.train_path.data.encode('utf-8')
    test_path = form.test_path.data.encode('utf-8')
    extra_parameter = form.extra_parameter.data
    cpu_count = form.cpu_count.data
    gpu_count = int(form.gpu_count.data)
    memory = form.memory_count.data
    node_count = form.node_count.data
    matchExpressions_values = form.node_label_choice.data
    max_run_time = form.max_run_time.data
    username = utils.auth.get_username()
    mount_path = config_value('jobs_dir')
    model_path = os.path.join(config_value('jobs_dir'), username+'/'+'code'+'/')
    server_path = form.server_path.data.encode('utf-8')
    caffe_path = form.caffe_path.data.encode('utf-8')
    gpu_tatol = int(gpu_count) * int(node_count)
    solver_path = form.solver_path.data.encode('utf-8')
    main_name = form.main_name.data.encode('utf-8')
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
                if file_name == main_name:
                    base_path = model_path.encode('utf-8') + file_name
                    file_path_str = str(base_path)
                else:
                    file_path = model_path.encode('utf-8') + file_name
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
                                 cpu_count=cpu_count)

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
                                                         data_dir=dataset_path,
                                                         train_dir=train_path,
                                                         test_dir=test_path,
                                                         framework=framework,
                                                         framework_version=frame_version,
                                                         model_dir=model_path,
                                                         mount_path=mount_path,
                                                         username=username,
                                                         extra_parameter=extra_parameter,
                                                         matchExpressions_values=matchExpressions_values,
                                                         ))

            save_form_to_job(job, form)
            scheduler.add_job(job)
        except:
            if job:
                scheduler.delete_job(job)
            raise
        return redirect(url_for('hyperai.vip.views.show', job_id=job.id()))
    elif framework == 'tensorflowmpi':
        mpitf_obj = MpiTensorflow('distributed_tensorflow', 'distributed')
        try:
            job = DistributedJob(username=utils.auth.get_username(),
                                 name=homework_name,
                                 mode='distributed',
                                 node_count=range(int(node_count)),
                                 framework=framework,
                                 cpu_count=cpu_count)

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
                data_dir=dataset_path,
                framework=framework,
                framework_version=frame_version,
                mount_path=mount_path,
                username=username,
                extra_parameter=extra_parameter,
                matchExpressions_values=matchExpressions_values,
            ))

            save_form_to_job(job, form)
            scheduler.add_job(job)
        except:
            if job:
                scheduler.delete_job(job)
            raise
        return redirect(url_for('hyperai.vip.views.show', job_id=job.id()))
    elif framework == 'tensorflow':
        native_tf_obj = NativeTensorflow('distributed_tensorflow', 'distributed')
        try:
            job = DistributedJob(username=utils.auth.get_username(),
                                 name=homework_name,
                                 mode='distributed',
                                 node_count=range(int(node_count)),
                                 framework="tensorflow",
                                 cpu_count=cpu_count)

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
                data_dir=dataset_path,
                framework=framework,
                framework_version=frame_version,
                mount_path=mount_path,
                username=username,
                extra_parameter=extra_parameter,
                matchExpressions_values=matchExpressions_values,
            ))

            save_form_to_job(job, form)
            scheduler.add_job(job)
        except:
            if job:
                scheduler.delete_job(job)
            raise
        return redirect(url_for('hyperai.vip.views.show', job_id=job.id()))
    else:
        pass


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
    form = VipForm()
    fill_form_if_cloned(form)
    framework = form.framework.data
    frame_version = form.frame_version.data
    homework_name = form.homework_name.data
    images_list = flask.request.files.getlist('image_list')
    extra_parameter = form.extra_parameter.data
    dataset_path = form.data_path.data.encode('utf-8')
    train_path = form.train_path.data.encode('utf-8')
    test_path = form.test_path.data.encode('utf-8')
    cpu_count = form.cpu_count.data
    gpu_count = form.gpu_count.data
    gpu_count = int(gpu_count)
    memory = form.memory_count.data
    node_count = 1
    matchExpressions_values = form.node_label_choice.data

    username = utils.auth.get_username()
    mount_path = config_value('jobs_dir')
    model_path = os.path.join(config_value('jobs_dir'), username+'/'+'code'+'/')
    gpu_tatol = int(gpu_count)
    max_run_time = form.max_run_time.data
    server_path = form.server_path.data.encode('utf-8')
    caffe_path = form.caffe_path.data.encode('utf-8')
    solver_path = form.solver_path.data.encode('utf-8')
    main_name = form.main_name.data.encode('utf-8')
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
    except Exception as e:
        print e
        return flask.make_response('文件上传失败')

    if not file_path:
            raise ValueError('The file is not exist!')
    if framework == "tensorflow":
        tf_obj = Tensorflow('tensorflow','single')
        job = DistributedJob(username=utils.auth.get_username(),
                             name=homework_name,
                             mode='single',
                             node_count=range(node_count),
                             framework=framework,
                             cpu_count=cpu_count,
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
                                              data_dir=dataset_path,
                                              framework=framework,
                                              framework_version=frame_version,
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
                             cpu_count=cpu_count)

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
                                                      data_dir=dataset_path,
                                                      train_dir=train_path,
                                                      test_dir=test_path,
                                                      framework=framework,
                                                      framework_version=frame_version,
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
                             cpu_count=cpu_count)

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
                                                     data_dir=dataset_path,
                                                     framework=framework,
                                                     framework_version=frame_version,
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
                             cpu_count=cpu_count)

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
                                                     data_dir=dataset_path,
                                                     framework=framework,
                                                     framework_version=frame_version,
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
                             cpu_count=cpu_count,)

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
            data_dir=dataset_path,
            framework=framework,
            framework_version=frame_version,
            mount_path=mount_path,
            username=username,
            extra_parameter=extra_parameter,
            matchExpressions_values=matchExpressions_values,
        ))
    else:
        pass
    save_form_to_job(job, form)
    scheduler.add_job(job)

    return redirect(url_for('hyperai.vip.views.show', job_id=job.id()))


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




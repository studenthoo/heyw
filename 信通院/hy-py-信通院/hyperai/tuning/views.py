#!/root/anaconda3/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-2017, NVIDIA CORPORATION. All rights reserved.
from __future__ import absolute_import

import hyperai
import os
import sys
import time
import glob
import json
from datetime import datetime
import flask

import werkzeug.exceptions
import subprocess
import platform
import re
from .form import TuneForm
from flask import Flask, render_template, request, redirect, url_for
from hyperai.config import config_value
from hyperai import utils
from hyperai.webapp import scheduler
from .job import ParaJob
from hyperai.tuning.task.train import ParaTrain
from hyperai.utils.forms import fill_form_if_cloned, save_form_to_job
from hyperai.utils.auth import requires_login
from hyperai.models import User
from hyperai.users import register_user
# from hyperai.ext import r

blueprint = flask.Blueprint(__name__, __name__)


@blueprint.route('/', methods=['GET'])
@requires_login
def new():
    form = TuneForm()
    fill_form_if_cloned(form)

    node_label_dict = scheduler.resources['gpus'].get_usable_label_gpu()
    label_gpu_value = [v for k, v in sorted(node_label_dict.items())]
    return render_template('new/tuning.html',
                           index='tuning',
                           form=form,
                           total_gpu_count=scheduler.resources['gpus'].get_gpu_max(),
                           remaining_gpu_count=scheduler.resources['gpus'].remaining(),
                           usable_label_gpu_count=label_gpu_value,
                           )


@blueprint.route('/check_res', methods=['GET'])
@requires_login
def check_resources():
    gpu_count = flask.request.args.get('gpu_count')
    cpu_count = flask.request.args.get('cpu_count')
    memory_count = flask.request.args.get('memory_count')
    username = flask.request.cookies.get('username')
    gpu_max = User.get_gpu_max(username)
    gpu_total = int(gpu_count)

    # check the resources about user
    res = register_user.is_enough_resource_about_user(username, gpu_total, gpu_max)
    print(res)
    if not res:
        num = register_user.get_used_resource_about_user(username)
        data = {'a': 0, 'res': '您的信息：可用GPU/申请GPU：{}/{}'.format((int(gpu_max) - num), int(gpu_total))}
        return flask.jsonify(data)
    elif res == 'Forbid':
        return flask.jsonify({'a': 0, 'res': '您已被管理员禁用，请尝试联系管理员'})
    else:
        return flask.jsonify({'a': 1})


@blueprint.route('/new', methods=['POST'])
@requires_login
def get_data():
    if request.method == 'POST':
        form = TuneForm()
        fill_form_if_cloned(form)
        homework_name = form.homework_name.data
        dataset_file = form.dataset_file.data.encode('utf-8')
        username = utils.auth.get_username()
        optimize_type = form.optimize_type.data.encode('utf-8')
        batch_size = form.batch_size.data.encode('utf-8')
        # 上传文件保存路径
        file_path = os.path.join(config_value('jobs_dir'), username+'/'+'code'+'/')
        cpu_count = form.cpu_count.data
        gpu_count = form.gpu_count.data
        memory_count = form.memory_count.data
        node_label = form.node_label_choice.data

        files = form.model_file.data
        server_path = form.model_path.data.encode('utf-8')
        # print optimize_type, server_path
        job = ParaJob(username=utils.auth.get_username(),
                      name=homework_name,
                      framework='ParaOPT',
                      cpu_count=cpu_count,
                     )

        # change the gpu_used about user
        # gpu_total = int(gpu_count)
        # if r.get("{}_gpu".format(username)) is not None:
        #     gpu_used = r.get("{}_gpu".format(username))
        # else:
        #     gpu_used = 0
        #
        # new_gpu_used = int(gpu_used) + gpu_total
        #
        # try:
        #     r.set("{}_gpu".format(username), new_gpu_used)
        # except Exception as e:
        #     print e


        if optimize_type == 'Bayesian optimization':
            # optimize_method = request.values.get('Bayesian_method').encode('utf-8')
            # bayesion_iteration = request.form.get('bayesion_iteration').encode('utf-8')
            # model_iteration = request.form.get('model_iteration').encode('utf-8')
            optimize_method = form.Bayesian_method.data.encode('utf-8')
            bayesion_iteration = form.bayesion_iteration.data.encode('utf-8')
            model_iteration = form.model_iteration.data.encode('utf-8')
        elif optimize_type == 'Population Based Training':
            optimize_method = request.values.get('optimize_method').encode('utf-8')
            epoch = request.form.get('epoch')
            worker_number = request.form.get('worker_number')
            exploit_interval = request.form.get('exploit_interval')
        if server_path:
            model_path = server_path
        else:
            if files:
                file_name = files.filename.encode('utf-8')
                # 建立软连接
                # link_dir = os.path.join(job.dir() + '/' + file_name)
                # print link_dir
                files.save(os.path.join(file_path, file_name))
                model_path = file_path.encode('utf-8') + file_name
                # os.symlink(model_path, link_dir)
        # print model_path
        if optimize_type == 'Bayesian optimization':
            momentum_lower = 0
            optional_para1 = []
            momentum_up = 0
            lr_lower = 0
            lr_up = 0

            # lr = request.values.get('lr', None).encode('utf-8')
            # momentum = request.values.get('momentum', None).encode('utf-8')
            # decay = request.values.get('decay', None).encode('utf-8')
            # beta1 = request.values.get('beta1', None).encode('utf-8')
            # beta2 = request.values.get('beta2', None).encode('utf-8')
            lr = form.lr.data.encode('utf-8')
            momentum = form.momentum.data.encode('utf-8')
            decay = form.decay.data.encode('utf-8')
            beta1 = form.beta1.data.encode('utf-8')
            beta2 = form.beta2.data.encode('utf-8')
            # print '=====================>', lr, momentum, decay, model_path, dataset_file, bayesion_iteration, model_iteration, optimize_method

            job.lr = lr
            job.momentum = momentum
            job.decay = decay
            job.beta1 = beta1
            job.beta2 = beta2

            if optimize_method == 'GD':
                job.method = 'GD'
                # lr_lower = request.values.get('lr_lower')
                # lr_up = request.values.get('lr_up')
                lr_lower = form.lr_lower.data
                lr_up = form.lr_up.data
            elif optimize_method == 'RMSProp':
                job.method = 'RMSProp'
                # lr_lower = request.values.get('lr_lower')
                # lr_up = request.values.get('lr_up')
                optional_para = request.values.getlist('optional_para')
                lr_lower = form.lr_lower.data
                lr_up = form.lr_up.data
                # optional_para = form.optional_para.data
                for i in optional_para:
                    i.encode('utf-8')
                    optional_para1.append(i.encode('utf-8'))
            elif optimize_method == 'Adam':
                job.method = 'Adam'
                optional_para = request.values.getlist('optional_para')
                # optional_para = form.optional_para.data
                for i in optional_para:
                    i.encode('utf-8')
                    optional_para1.append(i.encode('utf-8'))
            elif optimize_method == 'Momentum':
                job.method = 'Momentum'
                # lr_lower = request.values.get('lr_lower')
                # lr_up = request.values.get('lr_up')
                lr_lower = form.lr_lower.data
                lr_up = form.lr_up.data
                # momentum_lower = request.values.get('momentum_lower')
                # momentum_up = request.values.get('momentum_up')
                momentum_lower = form.momentum_lower.data
                momentum_up = form.momentum_up.data
            job.tasks.append(ParaTrain(
                optimize_type=optimize_type,
                optimize_method=optimize_method,
                model_path=model_path,
                dataset_file=dataset_file,
                batch_size=int(batch_size),
                bayesion_iteration=int(bayesion_iteration),
                model_iteration=int(model_iteration),
                optional_para1=optional_para1,
                lr_lower=float(lr_lower),
                lr_up=float(lr_up),
                momentum_lower=float(momentum_lower),
                momentum_up=float(momentum_up),
                lr=lr,
                momentum=momentum,
                decay=decay,
                beta1=beta1,
                beta2=beta2,
                gpu_count=gpu_count,
                cpu_count=cpu_count,
                memory_count=memory_count,
                node_label=node_label,
                job=job,
                framework='ParaOPT',
            ))
        else:
            lr = request.form.get('learning_rate')
            weight_decay = request.form.get('weight_decay')
            if optimize_method == 'SGD':
                momentum = request.form.get('momentum')
                dampening = request.form.get('dampening')
        scheduler.add_job(job)
        save_form_to_job(job, form)
        return redirect(url_for('hyperai.tuning.views.show', job_id=job.id()))


@blueprint.route('/<job_id>.json', methods=['GET'])
@blueprint.route('/<job_id>', methods=['GET'])
@requires_login
def show(job_id):
    job = scheduler.get_job(job_id)
    if job is None:
        raise werkzeug.exceptions.NotFound('Job not found')
    return render_template('/new/tuning-result.html', job=job)


# def run(args=None, job=None):
#     base_dir = os.path.dirname(os.path.abspath(__file__))
#     p = subprocess.Popen(args=args,
#                          stdout=subprocess.PIPE,
#                          stderr=subprocess.STDOUT,
#                          cwd=base_dir,
#                          close_fds=False if platform.system() == 'Windows' else True,
#                          )
#     try:
#         while p.poll() is None:
#             for line in utils.nonblocking_readlines(p.stdout):
#                 if line is not None:
#                     line = line.strip()
#                 if line:
#                     print line
#                     time.sleep(0.1)
#                     au_process_output(line, job)
#                     progress(line, job)
#                     sys.stdout.flush()
#     except Exception as e:
#         print(e)
#         p.terminate()

# def progress(line, job):
#     with open(os.path.join(job.dir(), 'tuning.log'), 'a+') as log:
#         log.write('%s\n' % line)
#         log.flush()


@blueprint.route('/show_log', methods=['GET', 'POST'])
@requires_login
def show_log():
    job_id = flask.request.args.get('job_id')
    username = utils.auth.get_username()
    log_dir = os.path.join(config_value('jobs_dir'), username, 'jobs', str(job_id))

    log_path = os.path.join(log_dir, 'au_ParaOPT_output.log')

    if os.path.exists(log_path):
        # print "Exist join log_path: ", log_path
        with open(log_path, 'rt') as logs:
            logs = logs.readlines()
            return flask.render_template('/new/tuning_log.html', logs=logs)
    else:
        return flask.make_response('The log is not exist!')


@blueprint.route('/download/<name>', methods=['GET'])
@requires_login
def download_log(name):
    """
    Return a file in the jobs directory
    If you install the nginx.site file, nginx will serve files instead
    and this path will never be used
    """
    job_id = flask.request.args.get('job_id')
    try:
        job_id
    except Exception as e:
        print e
        raise ValueError("No job_id !")

    username = utils.auth.get_username()
    log_dir = os.path.join(config_value('jobs_dir'), username, 'jobs', str(job_id))

    return flask.send_from_directory(log_dir, name, as_attachment=True)
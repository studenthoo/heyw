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
from flask import Flask, render_template, request, redirect, url_for, jsonify
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
    node_label_dict = scheduler.resources['gpus'].get_usable_label_gpu()
    new_node_label_dict = sorted(node_label_dict.items())
    data = {'clone': 'no', 'usable_label_gpu_count': new_node_label_dict, 'total_gpu_count': scheduler.resources['gpus'].get_gpu_max(),
            'remaining_gpu_count': scheduler.resources['gpus'].remaining(), 'index': 'tuning'}
    return flask.jsonify(data)
    # return render_template('new/tuning.html',
    #                        index='tuning',
    #                        form=form,
    #                        total_gpu_count=scheduler.resources['gpus'].get_gpu_max(),
    #                        remaining_gpu_count=scheduler.resources['gpus'].remaining(),
    #                        usable_label_gpu_count=label_gpu_value,
    #                        )


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


@blueprint.route('/new', methods=['POST'], strict_slashes=False)
@requires_login
def get_data():
    if request.method == 'POST':
        homework_name = request.form.get('homework_name')
        dataset_file = request.form.get('dataset_file').encode('utf-8')
        optimize_type = request.values.get('optimize_type').encode('utf-8')
        batch_size = request.form.get('batch_size')
        cpu_count = request.values.get('cpu_count')
        gpu_count = request.form.get('gpu_count')
        memory_count = request.values.get('memory_count')
        node_label = request.form.get('matchExpressions_values')
        files = request.files.get('model_file')
        server_path = request.form.get('server_path')
        username = utils.auth.get_username()
        file_path = os.path.join(config_value('jobs_dir'), username + '/' + 'code' + '/')
        optimize_method = request.values.get('Bayesian_method').encode('utf-8')
        bayesion_iteration = request.form.get('bayesion_iteration')
        model_iteration = request.form.get('model_iteration')

        job = ParaJob(username=username,
                      name=homework_name,
                      framework='ParaOPT',
                      cpu_count=cpu_count,
                      server_path=server_path,
                     )

        if server_path:
            model_path = server_path
        else:
            if files:
                file_name = files.filename.encode('utf-8')
                files.save(os.path.join(file_path, file_name))
                model_path = file_path.encode('utf-8') + file_name

        if optimize_type == 'Bayesian optimization':
            momentum_lower = 0
            optional_para1 = []
            momentum_up = 0
            lr_lower = 0
            lr_up = 0

            # lr = form.lr.data.encode('utf-8')
            # momentum = form.momentum.data.encode('utf-8')
            # decay = form.decay.data.encode('utf-8')
            # beta1 = form.beta1.data.encode('utf-8')
            # beta2 = form.beta2.data.encode('utf-8')
            lr = request.form.get('lr').encode('utf-8')
            momentum = request.form.get('momentum').encode('utf-8')
            decay = request.form.get('decay').encode('utf-8')
            beta1 = request.form.get('beta1').encode('utf-8')
            beta2 = request.form.get('beta2').encode('utf-8')

            print lr, momentum
            job.lr = lr
            job.momentum = momentum
            job.decay = decay
            job.beta1 = beta1
            job.beta2 = beta2

            if optimize_method == 'GD':
                job.method = 'GD'
                # lr_lower = form.lr_lower.data
                # lr_up = form.lr_up.data
                lr_lower = request.form.get('lr_lower')
                lr_up = request.form.get('lr_up')
            elif optimize_method == 'RMSProp':
                job.method = 'RMSProp'
                optional_para = request.values.getlist('optional_para')
                # lr_lower = form.lr_lower.data
                # lr_up = form.lr_up.data
                lr_lower = request.form.get('lr_lower')
                lr_up = request.form.get('lr_up')
                for i in optional_para:
                    i.encode('utf-8')
                    optional_para1.append(i.encode('utf-8'))
            elif optimize_method == 'Adam':
                job.method = 'Adam'
                optional_para = request.values.getlist('optional_para')
                for i in optional_para:
                    i.encode('utf-8')
                    optional_para1.append(i.encode('utf-8'))
            elif optimize_method == 'Momentum':
                job.method = 'Momentum'
                # lr_lower = form.lr_lower.data
                # lr_up = form.lr_up.data
                # momentum_lower = form.momentum_lower.data
                # momentum_up = form.momentum_up.data
                lr_lower = request.form.get('lr_lower')
                lr_up = request.form.get('lr_up')
                momentum_lower = request.form.get('momentum_lower')
                momentum_up = request.form.get('momentum_up')

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
        scheduler.add_job(job)
        data = {'job_id': job.id(), 'statue': job.train_task().status.name, 'create_time': str(job.create_time), 'end_time': str(job.end_time),
                'cost_time': str(job.cost_time), 'train_lr': job.train_lr, 'train_beta1': job.train_beta1, 'train_momentum': job.train_momentum,
                'train_beta2': job.train_beta2, 'train_decay': job.train_decay, 'method': job.method, 'lr': job.lr, 'decay': job.decay,
                'beta1': job.beta1, 'beta2': job.beta2, 'momentum': job.momentum}
        return jsonify(data)


@blueprint.route('/show', methods=['POST'])
@requires_login
def show():
    job_id = request.form.get('job_id')
    if job_id:
        job = scheduler.get_job(job_id)
        data = {"log": job.log_data(), 'end_time': str(job.end_time), 'cost_time': str(job.cost_time), 'train_lr': job.train_lr,
                'train_decay': job.train_decay, 'train_momentum': job.train_momentum, 'train_beta1': job.train_beta1, 'train_beta2': job.train_beta2, 'create_time': str(job.create_time),
                'statue': job.train_task().status.name, 'framework': job.framework, 'lr': job.lr, 'decay': job.decay, 'momentum': job.momentum,
                'beta1': job.beta1, 'beta2': job.beta2, 'method': job.method}
        return jsonify(data)
    else:
        pass


@blueprint.route('/show_log', methods=['GET', 'POST'])
@requires_login
def show_log():
    job_id = flask.request.args.get('job_id')
    username = utils.auth.get_username()
    log_dir = os.path.join(config_value('jobs_dir'), username, 'jobs', str(job_id))

    log_path = os.path.join(log_dir, 'au_ParaOPT_output.log')

    if os.path.exists(log_path):
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
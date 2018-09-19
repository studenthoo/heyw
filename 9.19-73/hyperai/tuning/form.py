#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-2017, NVIDIA CORPORATION.  All rights reserved.

import os

import flask
from flask.ext.wtf import Form
import wtforms
from wtforms import validators
import wtforms
from hyperai.config import config_value
from hyperai.device_query import get_device, get_nvml_info
from hyperai import utils
from hyperai.utils import sizeof_fmt
from hyperai.utils.forms import validate_required_iff


class TuneForm(Form):
    """
            single and vip form detail
    """
    homework_name = utils.forms.StringField(
        'homework_name'
    )

    model_file = utils.forms.FileField(
        'Model_file_path',
    )

    model_path = utils.forms.StringField(
        'The path of model_file on server',
        default=''
    )

    dataset_file = utils.forms.StringField(
        'The path of fataset on server',
    )

    cpu_count = utils.forms.SelectField(
        'Cpu count',
        choices=[
            ('2', '2'),
            ('4', '4'),
            ('8', '8'),

        ],
        default='4',
        tooltip="cup count used",
    )

    memory_count = utils.forms.SelectField(
        'Memory count',
        choices=[
             ('8G', '8G'),
             ('16G', '16G'),
             ('32G', '32G'),
        ],
        default='16G',
        tooltip="memory count used",
    )

    gpus_max_on_nodes = config_value('gpus_max_on_nodes')
    gpu_count = utils.forms.SelectField(
        'Gpu_count_new',
        choices=[('%d' % i, '%d' % i) for i in range(1, gpus_max_on_nodes + 1)],
        default=1
    )

    optimize_type = utils.forms.SelectField(
        'optimize_type',
        choices=[
            ('Bayesian optimization', 'Bayesian optimization'),
        ]
    )

    Bayesian_method = utils.forms.SelectField(
        'optimize_method',
        choices=[
            ('GD', 'GD'),
            ('RMSProp', 'RMSProp'),
            ('Adam', 'Adam'),
            ('Momentum', 'Momentum')
        ]
    )

    optimize_method = utils.forms.SelectField(
        'optimize_method',
        choices=[
            ('SGD', 'SGD'),
            ('Adam', 'Adam'),
        ]
    )
    optional_para = wtforms.BooleanField(
        'optional_para'
    )

    batch_size = utils.forms.StringField(
        'batch_size',
    )

    bayesion_iteration = utils.forms.StringField(
        'bayesion_iteration',
    )

    model_iteration = utils.forms.StringField(
        'model_iteration',
    )

    lr_up = utils.forms.StringField(
        'lr_up',
    )

    lr_lower = utils.forms.StringField(
        'lr_lower',
    )

    momentum_up = utils.forms.StringField(
        'momentum_up',
    )

    momentum_lower = utils.forms.StringField(
        'momentum_lower',
    )

    decay_up = utils.forms.StringField(
        'decay_up',
    )

    decay_lower = utils.forms.StringField(
        'decay_lower',
    )

    beta1_up = utils.forms.StringField(
        'beta1_up',
    )

    beta2_up = utils.forms.StringField(
        'beta2_up',
    )

    beta1_lower = utils.forms.StringField(
        'beta1_lower',
    )

    beta2_lower = utils.forms.StringField(
        'beta2_lower',
    )

    lr = wtforms.HiddenField(
        'lr',
    )

    momentum = wtforms.HiddenField(
        'momentum',
    )

    decay = wtforms.HiddenField(
        'decay',
    )

    beta1 = wtforms.HiddenField(
        'beta1',
    )

    beta2 = wtforms.HiddenField(
        'beta2',
    )
    from hyperai.webapp import scheduler
    node_label_dict = scheduler.resources['gpus'].get_usable_label_gpu()
    node_label_choice = wtforms.RadioField(
        'Node_Label',
        choices=[('%s' % k, '%s' % k) for k, v in sorted(node_label_dict.items())],
        default=sorted(node_label_dict.items())[0][0],
    )

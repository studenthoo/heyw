#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-2017, NVIDIA CORPORATION.  All rights reserved.

import os

import flask
from flask.ext.wtf import Form
import wtforms
from wtforms import validators

from hyperai.config import config_value
from hyperai.device_query import get_device, get_nvml_info
from hyperai import utils
from hyperai.utils import sizeof_fmt
from hyperai.utils.forms import validate_required_iff


class VipForm(Form):
    """
        single and vip form detail
    """
    # field
    homework_name = utils.forms.StringField(
        'Vip Name',
    )

    model_file = utils.forms.FileField(
        'Model_file_path',
    )

    # model_path = utils.forms.StringField(
    #     'aa'
    # )
    data_path = utils.forms.StringField(
        'The path of fataset on server',
        # validators=[
        #     validators.InputRequired()
        # ],
    )

    train_path = utils.forms.StringField(
        'The path of fataset on server',
        # validators=[
        #     validators.InputRequired()
        # ],
    )

    test_path = utils.forms.StringField(
        'The path of fataset on server',
        # validators=[
        #     validators.InputRequired()
        # ],
    )

    node_count = utils.forms.StringField(
        'Num of worker',
        default=1,
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
            ('8', '8G'),
            ('16', '16G'),
            ('32', '32G'),

        ],
        default='16',
        tooltip="memory count used",
    )

    gpus_max_on_nodes = config_value('gpus_max_on_nodes')
    gpu_count = utils.forms.SelectField(
        'Gpu_count_new',
        choices=[('%d' % i, '%d' % i) for i in range(1, gpus_max_on_nodes + 1)],
        default=1
    )

    extra_parameter = utils.forms.TextAreaField(
        'Extra_parameter',
    )

    # framework = wtforms.HiddenField(
    #     'use to chose tensorflow or caffe',
    #     default='tenssorflow',
    # )


    framework = utils.forms.SelectField(
        'Framework',
        choices=[
            ('tensorflow', 'tensorflow'),
        ],
        default="tensorflow",
    )

    frame_version = utils.forms.SelectField(
        'Frame Version',
        choices=[
            ('1.2.0', '1.2.0'),
        ],
        default="1.2.0",
    )
    max_run_time = utils.forms.StringField(
        'max_run_time',
        default='',
    )

    from hyperai.webapp import scheduler
    node_label_dict = scheduler.resources['gpus'].get_usable_label_gpu()
    node_label_choice = wtforms.RadioField(
        'Node_Label',
        choices=[('%s' % k, '%s' % k) for k, v in sorted(node_label_dict.items())],
        default=sorted(node_label_dict.items())[0][0],
    )

    server_path = utils.forms.StringField(
        'The path of model_file on server',
        default=''
    )

    caffe_path = utils.forms.StringField(
        'The path of model_file on server',
        default=''
    )

    solver_path = utils.forms.StringField(
        'The path of model_file on server',
        default=''
    )

    main_name = utils.forms.StringField(
        'The path of model_file on server',
        default=''
    )
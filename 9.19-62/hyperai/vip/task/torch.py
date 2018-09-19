#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-2017, NVIDIA CORPORATION.  All rights reserved.
from __future__ import absolute_import

import os
import sys
import subprocess
import platform
import flask
import hyperai
import re
import signal

# from hyperai.model.tasks.train import TrainTask
from hyperai import utils
from hyperai.webapp import socketio
from hyperai.task import Task
from hyperai.status import Status
from hyperai.utils import subclass, override
from collections import OrderedDict, namedtuple
from hyperai.tools.advanced_user.au_mpi_kuber_coordinate import KubernetasCoord
from hyperai.utils.resource_monitor import Monitor
import gevent
import gevent.event
import time
from hyperai.config import config_value
from .train import TrainTask



class Torch:
    def __init__(self, name, mode):
        self.name = name
        self.mode = mode

    def create_train_task(self, **kwargs):
        return TorchTrain(name=self.name,mode=self.mode, **kwargs)


@subclass
class TorchTrain(TrainTask):

    TORCH_LOG = 'au_torch_output.log'

    def __init__(self, **kwargs):
        print "torch kwargs :" ,kwargs
        super(TorchTrain, self).__init__(**kwargs)
        self.log_file = self.TORCH_LOG
        self.torch_log = None
        self.log = None

    def __getstate__(self):
        state = super(TorchTrain, self).__getstate__()

        # Don't pickle these things
        if 'log' in state:
            del state['log']

        return state

    def __setstate__(self, state):
        super(TorchTrain, self).__setstate__(state)


    @override
    def before_run(self):
        self.log = open(self.path(self.TORCH_LOG), 'a+')
        self.graph_data_txt = open(self.path(self.GRAPH_DATA_TXT), 'a+')

        self.args = ['th',
                     self.file_path,
                     ]

        self.extra_parameter = str(self.extra_parameter).strip()
        if re.search(r"\r\n", self.extra_parameter):
            self.extra_parameter_list = self.extra_parameter.split("\r\n")
        else:
            self.extra_parameter_list = [self.extra_parameter]
        for i in self.extra_parameter_list:
            if len(i) == 0:
                self.extra_parameter_list.pop(self.extra_parameter_list.index(i))

        self.args.extend(self.extra_parameter_list)
        print "args: %s" % (' '.join(self.args))
        try:
            kube_cood = KubernetasCoord(self.logger,
                                        self.log,
                                        job=self.job,
                                        task_obj=self,
                                        mode=self.mode,
                                        job_id=self.job_id,
                                        job_dir=self.job_dir,
                                        gpu=self.gpu_count,
                                        cpu=self.cpu_count,
                                        memory=self.memory,
                                        node=self.node_count,
                                        image=self.image,
                                        framework=self.framework,
                                        args=self.args,
                                        matchExpressions_values=self.node_label,
                                        )
            pod_name = kube_cood.container_prepare(job_id=self.job_id)
            monitor = Monitor(self.job)
            self._hw_socketio_thread = gevent.spawn(monitor.hw_socketio_updater, self.job_id)
            return pod_name
        except Exception as e:
            self.status = Status.ERROR
            self.log.write("Container Create Failed: %s" % e)
            raise IOError("Container Create Failed: %s" % e)

    def middle_run(self, line):
        self.log.write('%s\n' % line)
        self.log.flush()

    @override
    def after_run(self):
        self.log.write("----*----delete pod ----*----")
        KubernetasCoord.delete_pods(job_id=self.job_id)
        self.log.close()
        self.graph_data_txt.close()
        super(TorchTrain, self).after_run()



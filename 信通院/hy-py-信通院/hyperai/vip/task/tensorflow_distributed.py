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

sys.path.insert(0, os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from hyperai import utils
from hyperai.webapp import socketio
from hyperai.task import Task
from hyperai.status import Status
from hyperai.utils import subclass, override
from collections import OrderedDict, namedtuple
from hyperai.tools.advanced_user.au_mpi_kuber_coordinate import KubernetasCoord
from hyperai.config import config_value
from hyperai.utils.resource_monitor import Monitor
import gevent
import gevent.event
import time
from .train import TrainTask


class Tensorflow:
    def __init__(self, name, mode):
        self.name = name
        self.mode = mode

    def create_train_task(self, **kwargs):
        return DistributedTrain(name=self.name,mode=self.mode, **kwargs)


@subclass
class DistributedTrain(TrainTask):

    TENSORFLOW_LOG = 'au_tensorflow_output.log'

    def __init__(self, **kwargs):
        super(DistributedTrain, self).__init__(**kwargs)
        self.log_file = self.TENSORFLOW_LOG
        self.log = None

    def __getstate__(self):
        state = super(DistributedTrain, self).__getstate__()

        # Don't pickle these things
        if 'log' in state:
            del state['log']
        if 'au_worker_log' in state:
            del state['au_worker_log']

        return state

    def __setstate__(self, state):
        super(DistributedTrain, self).__setstate__(state)


    @override
    def before_run(self):
        if self.mode == "single":
            self.log = open(self.path(self.TENSORFLOW_LOG), 'a+')
            self.graph_data_txt = open(self.path(self.GRAPH_DATA_TXT), 'a+')

        self.args = ['python',
                self.file_path,
                '--model_dir=%s' % self.model_dir,
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

    def middle_run(self,line):
        if self.mode == "single":
            self.log.write('%s\n' % line)
            self.log.flush()


    @override
    def after_run(self):
        if self.mode == "single":
            self.log.write("----*----delete pod ----*----")
            KubernetasCoord.delete_pods(job_id=self.job_id)
            self.log.close()
            self.graph_data_txt.close()

        super(DistributedTrain, self).after_run()



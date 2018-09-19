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


class Mxnet:
    def __init__(self, name, mode):
        self.name = name
        self.mode = mode

    def create_train_task(self, **kwargs):
        return MxnetTrain(name=self.name,mode=self.mode, **kwargs)


@subclass
class MxnetTrain(TrainTask):

    MXNET_LOG = 'au_mxnet_output.log'

    def __init__(self, **kwargs):
        super(MxnetTrain, self).__init__(**kwargs)
        self.log_file = self.MXNET_LOG
        self.log = None
        self.temp_dict = {}
        self.speed = None
        self.step = 0

    def __getstate__(self):
        state = super(MxnetTrain, self).__getstate__()

        # Don't pickle these things
        if 'log' in state:
            del state['log']

        return state

    def __setstate__(self, state):
        super(MxnetTrain, self).__setstate__(state)


    @override
    def before_run(self):
        self.log = open(self.path(self.MXNET_LOG), 'a+')
        self.graph_data_txt = open(self.path(self.GRAPH_DATA_TXT), 'a+')

        self.args = ['python',
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
            # print(kube_cood)
            pod_name = kube_cood.container_prepare(job_id=self.job_id)
            monitor = Monitor(self.job)
            self._hw_socketio_thread = gevent.spawn(monitor.hw_socketio_updater, self.job_id)
            return pod_name
        except Exception as e:
            self.status = Status.ERROR
            self.job.state = 2
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
        super(MxnetTrain, self).after_run()

    def au_process_output(self, line):
        socketio.emit('log',
                      {
                          'task': 'log',
                          'update': 'log_data',
                          'data': line,
                      },
                      namespace='/jobs',
                      room=self.job_id,
                      )
        self.middle_run(line)
        data_line = self.regular_train_output(line)
        if not data_line:
            return 'No regular data line'
        if data_line:
            if data_line.get('epoch') and data_line.get('batch'):
                self.temp_dict['train_accuracy'] = data_line.get('accuracy').encode('utf-8')
                self.temp_dict['speed'] = data_line.get('speed').encode('utf-8')
                self.speed = data_line.get('speed').encode('utf-8')
            elif data_line.get('name') == "Train":
                self.temp_dict['train_accuracy'] = data_line.get('value').encode('utf-8')
            elif data_line.get('name') == "Validation":
                self.temp_dict['val_accuracy'] = data_line.get('value').encode('utf-8')
                self.temp_dict['val_epoch'] = self.step
                self.temp_dict['speed'] = self.speed

            if len(self.temp_dict) > 1:
                self.temp_dict['epoch'] = self.step
                self.graph_data_txt.write('%s\n' % self.temp_dict)
                self.graph_data_txt.flush()
                socketio.emit('task update',
                              {
                                  'task': 'vip_job',
                                  'update': 'accuracy_graph',
                                  'data': self.temp_dict,
                              },
                              namespace='/jobs',
                              room=self.job_id,
                              )
                self.temp_dict = {}
                self.step = self.step + 1
            else:
                pass

    def regular_train_output(self, line, cull=True):
        data_dict = {}
        line_pattern = re.compile(r"(INFO:)(\w+):Epoch\[(\d+)\] Batch \[(\d+)\](\s+)Speed: (\d+.\d+|\d+) samples/sec(\s+)(\w+)=(\d+.\d+|\d+)")
        data_line = re.search(line_pattern, line)
        if data_line:
            epoch = data_line.group(3)
            batch = data_line.group(4)
            speed = data_line.group(6)
            accuracy = data_line.group(9)
            data_dict['epoch'] = epoch
            data_dict['batch'] = batch
            data_dict['speed'] = speed
            data_dict['accuracy'] = accuracy
            return data_dict

        line_pattern2 = re.compile(r"(INFO:)(\w+):Epoch\[(\d+)\] (Train)(\S+)=(\d+.\d+)")
        data_line = re.search(line_pattern2, line)
        if data_line:
            val_epoch = data_line.group(3)
            name = data_line.group(4)
            value = data_line.group(6)
            data_dict['name'] = name
            data_dict['value'] = value
            data_dict['val_epoch'] = val_epoch
            return data_dict

        line_pattern3 = re.compile(r"(INFO:)(\w+):Epoch\[(\d+)\] (Validation)(\S+)=(\d+.\d+)")
        data_line = re.search(line_pattern3, line)
        if data_line:
            val_epoch = data_line.group(3)
            name = data_line.group(4)
            value = data_line.group(6)
            data_dict['name'] = name
            data_dict['value'] = value
            data_dict['val_epoch'] = val_epoch
            return data_dict
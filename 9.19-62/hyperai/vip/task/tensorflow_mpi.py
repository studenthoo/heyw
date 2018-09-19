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
# from hyperai.model.tasks.train import TrainTask
from hyperai.webapp import socketio
from hyperai.task import Task
from hyperai.status import Status
from hyperai.utils import subclass, override
from collections import OrderedDict, namedtuple
from hyperai.utils import subclass, override, constants
from hyperai.tools.advanced_user.au_mpi_kuber_coordinate import KubernetasCoord
from hyperai.config import config_value
import gevent
from hyperai.utils.resource_monitor import Monitor
import gevent.event
import time
from .train import TrainTask


class MpiTensorflow:
    def __init__(self, name, mode):
        self.name = name
        self.mode = mode

    def create_train_task(self, **kwargs):
        return MpiDistributedTrain(name=self.name, mode=self.mode, **kwargs)


@subclass
class MpiDistributedTrain(TrainTask):

    TENSORFLOW_LOG = 'au_tensorflowmpi_output.log'
    # GRAPH_DATA_TXT = 'au_graph_data.txt'
    AU_MPI_LOG = 'au_mpi.log'

    def __init__(self, **kwargs):
        print "tf mpi kwargs :", kwargs
        super(MpiDistributedTrain, self).__init__(**kwargs)
        self.log = None
        

    def __getstate__(self):
        state = super(MpiDistributedTrain, self).__getstate__()

        # Don't pickle these things
        if 'log' in state:
            del state['log']
        if 'au_worker_log' in state:
            del state['au_worker_log']

        return state

    def __setstate__(self, state):
        super(MpiDistributedTrain, self).__setstate__(state)


    @override
    def before_run(self):
        self.log = open(self.path(self.TENSORFLOW_LOG), 'a+')
        self.graph_data_txt = open(self.path(self.GRAPH_DATA_TXT), 'a+')
        self.args = ["no need"]
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
        super(MpiDistributedTrain, self).after_run()


    @override
    def task_arguments(self, resources, env, full_pod_name=None):
        if self.mode == "single":
            self.node_count = 1
        host_file = os.path.join(self.job_dir, 'hostfile')
        with open(host_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                new_line = line.strip()
                import re
                if re.search(r'(\S+)\s', new_line):
                    ip = re.search(r'(\S+)\s', new_line).group(1)

        args = ['kubectl exec %s --' % full_pod_name,
                '/usr/local/mpi/bin/mpirun',
                '-np', '%d' % (self.node_count * int(self.gpu_count)),
                '-hostfile', os.path.join(self.job_dir, 'hostfile'),
                '-bind-to', 'none',
                '-map-by', 'slot',
                '--allow-run-as-root',
                '-x', 'NCCL_DEBUG=INFO',
                '-x', 'LD_LIBRARY_PATH',
                "python",
                self.file_path,
                "--model_dir=%s" % self.model_dir,
                ]
        self.extra_parameter = str(self.extra_parameter).strip()
        if re.search(r"\r\n", self.extra_parameter):
            self.extra_parameter_list = self.extra_parameter.split("\r\n")
        else:
            self.extra_parameter_list = [self.extra_parameter]
        for i in self.extra_parameter_list:
            if len(i) == 0:
                self.extra_parameter_list.pop(self.extra_parameter_list.index(i))

        args.extend(self.extra_parameter_list)
        new_args = args
        resources_args = {}
        if self.gpu_count:
            resources_args['gpu_count'] = self.gpu_count
        if self.cpu_count:
            resources_args['cpu_count'] = self.cpu_count
        if self.memory:
            resources_args['memory_count'] = self.memory
        if self.node_count:
            resources_args['node_count'] = self.node_count

        return new_args, resources_args


    def regular_train_output(self,line):
        data_dict = {}

        message = self.preprocess_output_mpi(line)
        if not message:
            return None

        pattern_key_val = re.compile(r'([\w]+)\s=\s([^,^\s]+)')
        kvlist = re.findall(pattern_key_val, message.strip())
        if kvlist:
            for (key, value) in kvlist:
                value = float(value)
                if key == "loss":
                    data_dict["loss"] = value
                elif key == "step":
                    data_dict["step"] = value
                elif key == "accuracy":
                    data_dict["accuracy"] = value
                else:
                    pass

            return data_dict
        else:
            return None

    def preprocess_output_mpi(self,line):
        match = re.match(r'INFO:tensorflow:([\s\S]+)(\s*\((.*)\))?', line)
        if match:
            msg = match.group(1)
            return msg
        else:
            return None


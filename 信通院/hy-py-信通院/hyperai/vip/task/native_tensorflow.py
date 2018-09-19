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
from multiprocessing import Process

sys.path.insert(0, os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from hyperai import utils
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
from hyperai.utils import read_process_stdout


class NativeTensorflow:
    def __init__(self, name, mode):
        self.name = name
        self.mode = mode

    def create_train_task(self, **kwargs):
        return NativeDistributedTrain(name=self.name, mode=self.mode, **kwargs)


@subclass
class NativeDistributedTrain(TrainTask):
    TENSORFLOW_LOG = 'au_tensorflow_output.log'

    def __init__(self, **kwargs):
        super(NativeDistributedTrain, self).__init__(**kwargs)
        self.ip_list = []
        self.pod_list = []
        self.args = None
        self.log = None

    def __getstate__(self):
        state = super(NativeDistributedTrain, self).__getstate__()
        if 'log' in state:
            del state['log']
        return state

    def __setstate__(self, state):
        super(NativeDistributedTrain, self).__setstate__(state)

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
            self.pod_list, self.ip_list = kube_cood.container_prepare(job_id=self.job_id)
            monitor = Monitor(self.job)
            self._hw_socketio_thread = gevent.spawn(monitor.hw_socketio_updater, self.job_id)
            return True
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
        super(NativeDistributedTrain, self).after_run()

    @override
    def task_arguments(self, resources, env, i):
        ps_ip = self.ip_list[0] + ':12222'
        worker_ip = ''
        for j, worker in enumerate(self.ip_list[1:]):
            if (j + 2) < len(self.ip_list):
                worker_ip += self.ip_list[j + 1] + ':1222{},'.format(j + 2)
            else:
                worker_ip += self.ip_list[j + 1] + ':1222{}'.format(j + 2)
        if i == 0:
            args = ["kubectl exec {} -- python {} --task_index={} --job_name={} --parameter_servers={} "
                                "--worker={} --log_dir={}".format(self.pod_list[0], self.file_path, 0, 'ps', ps_ip, worker_ip, self.model_dir)]
        else:
            args = ["kubectl exec {} -- python {} --task_index={} --job_name={} --parameter_servers={} "
                    "--worker={} --log_dir={}".format(self.pod_list[i], self.file_path, (i-1), 'worker', ps_ip, worker_ip, self.model_dir)]
        new_args = args
        # 新返回的参数
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

    def run(self, resources, **kwargs):
        self.sch_obj = kwargs['sch_obj']
        self.before_run()
        env = os.environ.copy()
        self.status = Status.RUN
        base_dir = os.path.dirname(os.path.abspath(__file__))
        for i, pod in enumerate(self.pod_list):
            args, resources_args = self.task_arguments(resources, env, i)
            if not args:
                self.status = Status.ERROR
                return False
            print "args: %s" % (' '.join(self.args))
            if i != 1:
                p = subprocess.Popen(args=args,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     cwd=base_dir,
                                     close_fds=False if platform.system() == 'Windows' else True,
                                     env=env,
                                     shell=True,
                                     )
            else:
                self.args = args

        self.p = subprocess.Popen(args=self.args,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT,
                                  cwd=base_dir,
                                  close_fds=False if platform.system() == 'Windows' else True,
                                  env=env,
                                  shell=True,
                                  )
        try:
            sigterm_time = None
            sigterm_timeout = 2
            while self.p.poll() is None:
                for line in utils.nonblocking_readlines(self.p.stdout):
                    if self.aborted.is_set():
                        print("Torch Abort Enter")
                        if sigterm_time is None:
                            self.p.send_signal(signal.SIGTERM)
                            sigterm_time = time.time()
                            self.status = Status.ABORT
                        break
                    if line is not None:
                        line = line.strip()
                    if line:
                        time.sleep(0.1)
                        self.au_process_output(line)
                        sys.stdout.flush()
                    else:
                        time.sleep(0.05)

                if sigterm_time is not None and (time.time() - sigterm_time > sigterm_timeout):
                    self.p.send_signal(signal.SIGKILL)
                    self.logger.warning('Sent SIGKILL to task "%s"' % self.name())
                    time.sleep(0.1)
                time.sleep(0.01)
        except Exception as e:
            print e
            self.p.terminate()
        self.after_run()
        if self.status != Status.ABORT:
            self.judge_status()

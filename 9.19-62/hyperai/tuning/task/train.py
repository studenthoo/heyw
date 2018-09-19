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
import gevent
import gevent.event
import time

from datetime import datetime
from hyperai import utils
from hyperai.webapp import socketio
from hyperai.task import Task
from hyperai.status import Status
from hyperai.utils import subclass, override
from collections import OrderedDict, namedtuple
from hyperai.tools.tuning.kube import KubernetasCoord
from hyperai.config import config_value
from hyperai.utils.resource_monitor import Monitor
from hyperai.users import register_user


@subclass
class ParaTrain(Task):
    TUNE_LOG = 'au_ParaOPT_output.log'

    def __init__(self, **kwargs):
        self.job = kwargs['job']
        super(ParaTrain, self).__init__(job_dir=self.job.dir())
        self.optimize_type = kwargs['optimize_type']
        self.optimize_method = kwargs['optimize_method']
        self.model_dir = kwargs['model_path']
        self.data_dir = kwargs['dataset_file']
        self.batch_size = kwargs['batch_size']
        self.bayesion_iteration = kwargs['bayesion_iteration']
        self.model_iteration = kwargs['model_iteration']
        self.optional_para1 = kwargs['optional_para1']
        self.lr_lower = kwargs['lr_lower']
        self.lr_up = kwargs['lr_up']
        self.momentum_lower = kwargs['momentum_lower']
        self.momentum_up = kwargs['momentum_up']
        self.lr = kwargs['lr']
        self.momentum = kwargs['momentum']
        self.decay = kwargs['decay']
        self.beta1 = kwargs['beta1']
        self.beta2 = kwargs['beta2']
        self.cpu_count = kwargs['cpu_count']
        self.gpu_count = kwargs['gpu_count']
        self.memory = kwargs['memory_count']
        self.node_label = kwargs['node_label']

        self.node_count = 1
        self.image = config_value('img_main')
        self.status = Status.INIT
        self.aborted = gevent.event.Event()
        self.framework = kwargs['framework']
        self.framework_id = self.framework
        self.status = Status.INIT
        self.dbs = None

        register_user.allocate_resources(self.job.username, self)

    def __getstate__(self):
        state = super(ParaTrain, self).__getstate__()

        # Don't pickle these things
        if 'labels' in state:
            del state['labels']
        if 'image_mean' in state:
            del state['image_mean']
        if 'classifier' in state:
            del state['classifier']
        if 'tune_log' in state:
            del state['tune_log']
        if '_hw_socketio_thread' in state:
            del state['_hw_socketio_thread']
        if 'sch_obj' in state:
            del state['sch_obj']
        return state

    def __setstate__(self, state):
        super(ParaTrain, self).__setstate__(state)

        # Make changes to self
        self.loaded_snapshot_file = None
        self.loaded_snapshot_epoch = None

        # These things don't get pickled
        self.image_mean = None
        self.classifier = None

    def get_framework_id(self):
        """
        Returns a string
        """
        return self.framework_id

    def pre_allocate_res_task(self):
        if hasattr(self, 'sch_obj') and self.sch_obj:
            requested_resources = {'gpus': (self.sch_obj.resources['gpus'], self.gpu_count)}
            try:
                self.sch_obj.reserve_resources(self, requested_resources)
            except Exception as e:
                self.sch_obj.task_error(self, e)
                self.after_run()
                raise ValueError("Failed to allocate resource.")
            return True
        else:
            return False


    @override
    def before_run(self):
        self.tune_log = open(self.path(self.TUNE_LOG), 'a+')
        self.args = ['python',
                     self.model_dir,
                     '--data_dir=%s' % self.data_dir,
                     '--optimize_type=%s' % self.optimize_type,
                     '--optimize_method=%s' % self.optimize_method,
                     '--model_dir=%s' % self.job_dir.encode('utf-8'),
                     '--batch_size=%d' % self.batch_size,
                     '--bayesion_iteration=%d' % self.bayesion_iteration,
                     '--model_iteration=%d' % self.model_iteration,
                     '--optional_para1=%s' % self.optional_para1,
                     '--lr_lower=%.5f' % self.lr_lower,
                     '--lr_up=%.5f' % self.lr_up,
                     '--momentum_lower=%.5f' % self.momentum_lower,
                     '--momentum_up=%.5f' % self.momentum_up,
                     '--lr=%s' % self.lr,
                     '--momentum=%s' % self.momentum,
                     '--decay=%s' % self.decay,
                     '--beta1=%s' % self.beta1,
                     '--beta2=%s' % self.beta2,
                     ]
        print "args: %s" % (' '.join(self.args))
        try:
            kube_cood = KubernetasCoord(self.logger,
                                        job_id=self.job_id,
                                        task_obj=self,
                                        job_dir=self.job_dir,
                                        gpu=self.gpu_count,
                                        cpu=self.cpu_count,
                                        memory=self.memory,
                                        node=self.node_count,
                                        image=self.image,
                                        args=self.args,
                                        )
            pod_name = kube_cood.container_prepare(job_id=self.job_id)
            monitor = Monitor(self.job)
            self._hw_socketio_thread = gevent.spawn(monitor.hw_socketio_updater, self.job_id)
            return pod_name
        except Exception as e:
            self.status = Status.ERROR
            raise IOError("Container Create Failed: %s" % e)

    def middle_run(self, line):
        self.tune_log.write('%s\n' % line)
        self.tune_log.flush()

    @override
    def after_run(self):
        KubernetasCoord.delete_pods(job_id=self.job_id)
        self.tune_log.close()
        if hasattr(self, '_hw_socketio_thread'):
            self._hw_socketio_thread.kill()

    @override
    def offer_resources(self, resources, locking_gpu=False):
        if locking_gpu:
            return None
        gpu_count = int(self.gpu_count)
        if 'gpus' not in resources:
            return None
        if not resources['gpus']:
            return {}  # don't use a GPU at all
        if gpu_count is not None:
            if resources['gpus'].remaining():
                return {'gpus': (resources['gpus'], int(gpu_count))}
        return None

    @override
    def task_arguments(self, resources, env):

        args = ['python',
                '--data_dir=%s' % self.data_dir,
                ]
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

    def ready_to_queue(self):
        return True

    @override
    def run(self, resources, **kwargs):
        self.sch_obj=kwargs['sch_obj']

        full_pod_name = self.before_run()
        env = os.environ.copy()
        args, resources_args = self.task_arguments(resources, env)
        if not args:
            self.status = Status.ERROR
            return False
        self.status = Status.RUN
        base_dir = os.path.dirname(os.path.abspath(__file__))
        args = ["kubectl logs -f %s" % (full_pod_name)]
        print "args: ", args

        self.p = subprocess.Popen(args=args,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT,
                                  cwd=base_dir,
                                  close_fds=False if platform.system() == 'Windows' else True,
                                  env=env,
                                  shell=True,
                                  )
        try:
            sigterm_time = None  # When was the SIGTERM signal sent
            sigterm_timeout = 2  # When should the SIGKILL signal be sent
            while self.p.poll() is None:
                for line in utils.nonblocking_readlines(self.p.stdout):
                    if self.aborted.is_set():
                        if sigterm_time is None:
                            # Attempt graceful shutdown
                            self.p.send_signal(signal.SIGTERM)
                            sigterm_time = time.time()
                            self.status = Status.ABORT
                        break
                    if line is not None:
                        line = line.strip()
                    if line:
                        # print line
                        self.au_process_output(line)
                        sys.stdout.flush()
                    else:
                        time.sleep(0.01)
                if sigterm_time is not None and (time.time() - sigterm_time > sigterm_timeout):
                    self.p.send_signal(signal.SIGKILL)
                    self.logger.warning('Sent SIGKILL to task "%s"' % self.name())
                    time.sleep(0.1)
                time.sleep(0.01)
        except Exception as e:
            print "Def Run Exception : ", e
            self.p.terminate()
        self.after_run()
        if self.status != Status.ABORT:
            self.judge_status()

    def au_process_output(self, line):
        socketio.emit('log',
                      {
                          'task': 'log',
                          'update': 'log_data',
                          'data': line,
                      },
                      room=self.job_id,
                      namespace='/jobs',
                      )
        self.middle_run(line)
        data_line = self.regular_train_output(line)
        train_output = {}
        if data_line:
            for i in data_line:
                # print i
                if self.job.method == 'GD':
                    train_output['method'] = 'GD'
                    for lr in i:
                        train_output['lr'] = lr
                        self.job.train_lr = lr
                elif self.job.method == 'Momentum':
                    train_output['method'] = 'Momentum'
                    for index, data in enumerate(i):
                        if index == 0:
                            train_output['lr'] = data
                            self.job.train_lr = data
                        else:
                            train_output['momentum'] = data
                            self.job.train_momentum = data
                elif self.job.method == 'RMSProp':
                    train_output['method'] = 'RMSProp'
                    for index, data in enumerate(i):
                        if index == 0:
                            train_output['lr'] = data
                            self.job.train_lr = data
                        else:
                            if len(i) > 2:
                                if index == 1:
                                    train_output['momentum'] = data
                                    self.job.train_momentum = data
                                else:
                                    train_output['decay'] = data
                                    self.job.train_decay = data
                            else:
                                if self.job.momentum:
                                    train_output['momentum'] = data
                                    self.job.train_momentum = data
                                else:
                                    train_output['decay'] = data
                                    self.job.train_decay = data
                else:
                    train_output['method'] = 'Adam'
                    for index, data in enumerate(i):
                        if len(i) == 3:
                            if index == 0:
                                train_output['lr'] = data
                                self.job.train_lr = data
                            elif index == 1:
                                train_output['beta1'] = data
                                self.job.train_beta1 = data
                            elif index == 2:
                                train_output['beta2'] = data
                                self.job.train_beta2 = data
                        elif len(i) == 2:
                            if self.job.lr and self.job.beta1 and not self.job.beta2:
                                if index == 0:
                                    train_output['lr'] = data
                                    self.job.train_lr = data
                                else:
                                    train_output['beta1'] = data
                                    self.job.train_beta1 = data
                            elif self.job.lr and not self.job.beta1 and self.job.beta2:
                                if index == 0:
                                    train_output['lr'] = data
                                    self.job.train_lr = data
                                else:
                                    train_output['beta2'] = data
                                    self.job.train_beta2 = data
                            elif not self.job.lr and self.job.beta1 and self.job.beta2:
                                if index == 0:
                                    train_output['beta1'] = data
                                    self.job.train_beta1 = data
                                else:
                                    train_output['beta2'] = data
                                    self.job.train_beta2 = data
                        else:
                            if self.job.lr:
                                train_output['lr'] = data
                                self.job.train_lr = data
                            elif self.job.beta1:
                                train_output['beta1'] = data
                                self.job.train_beta1 = data
                            else:
                                train_output['beta2'] = data
                                self.job.train_beta1 = data
            end_time = datetime.now()
            self.job.end_time = end_time
            train_output['end_time'] = str(end_time)
            cost_time = end_time - self.job.begin_time
            self.job.cost_time = cost_time
            train_output['cost_time'] = str(cost_time)
            train_output['status'] = self.status.name
            print "socketio line: ", train_output
            socketio.emit('tuningdata',
                          {
                              'task': 'tune_job',
                              'update': 'accuracy_graph',
                              'data': train_output,
                          },
                          namespace='/jobs',
                          room=self.job.id(),
                          )

    def regular_train_output(self, line):
        line_pattern = re.compile(r"x: ([a-z]+)(.*)")
        data_line = re.search(line_pattern, line)
        if data_line:
            self.status = Status.DONE
            data_line = eval(data_line.group(2))
            return data_line

    def judge_status(self):
        log_dir = os.path.join(config_value('jobs_dir'), self.job.username, 'jobs', str(self.job_id))
        single_log_path = os.path.join(log_dir, "au_%s_output.log" % (self.job.framework))
        if os.path.exists(str(single_log_path)):
            with open(str(single_log_path), 'r+') as file:
                for line in file.readlines():
                    log_pattern = re.compile(r"Done|done")
                    regular_line = re.match(log_pattern, line)
                    if regular_line:
                        self.status = Status.DONE
                        return
                self.status = Status.ERROR
        else:
            self.status = Status.ERROR

    def abort(self):
        """
        Abort the Task
        """
        self.status = Status.ABORT
        self.aborted.set()
        pod_list = self.get_status(self.job_id)
        if pod_list:
            KubernetasCoord.delete_pods(job_id=self.job_id)

    def get_status(self, job_id):
        output = KubernetasCoord.short_exec_com()
        pod_list = KubernetasCoord.parse_pod_msg(element=job_id, content=output)
        return pod_list
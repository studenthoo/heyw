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
from hyperai.users import register_user

@subclass
class TrainTask(Task):

    GRAPH_DATA_TXT = 'au_graph_data.txt'
    AU_WORKER_LOG = 'au_worker_0.log'

    def __init__(self, **kwargs):
        self.job = kwargs['job']
        super(TrainTask, self).__init__(job_dir=self.job.dir())
        self.name = kwargs['name']
        self.mode = kwargs['mode']
        self.node_count = int(kwargs['node_count'])
        self.file_path = kwargs['file_path']
        self.gpu_count = kwargs['gpu_count']
        self.gpu_count = int(kwargs['gpu_count'])
        self.cpu_count = kwargs['cpu_count']
        self.memory = kwargs['memory']
        self.flag = "vip"
        self.status = Status.INIT
        self.data_dir = kwargs['data_dir']
        self.dbs = None
        self.model_dir = self.job_dir.encode('utf-8')
        self.train_outputs = []
        self.framework = kwargs['framework']
        self.framework_version = kwargs['framework_version']
        self.image = config_value('img_mysql_ip') + ':'+ config_value('img_vip_port')+ "/hyperai/" + self.framework + "_" + self.framework_version + ":latest"
        self.mount_path = kwargs['mount_path']
        self.username = kwargs['username']
        self.extra_parameter = kwargs['extra_parameter']
        self.p = None
        self.aborted = gevent.event.Event()
        self.graph_data_file = self.GRAPH_DATA_TXT
        self.au_worker_file = self.AU_WORKER_LOG
        self.au_worker_log = None
        self.graph_data_txt = None
        self.framework_id = self.framework
        self.node_label = kwargs['matchExpressions_values']

        register_user.allocate_resources(self.job.username, self)

    def __getstate__(self):
        state = super(TrainTask, self).__getstate__()

        # Don't pickle these things
        if 'labels' in state:
            del state['labels']
        if 'image_mean' in state:
            del state['image_mean']
        if 'classifier' in state:
            del state['classifier']
        if 'graph_data_txt' in state:
            del state['graph_data_txt']
        if '_hw_socketio_thread' in state:
            del state['_hw_socketio_thread']
        if 'matchExpressions_values' in state:
            del state['matchExpressions_values']
        if 'sch_obj' in state:
            del state['sch_obj']

        return state

    def __setstate__(self, state):
        super(TrainTask, self).__setstate__(state)

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
        # requested_resources = {'gpus': (resources['gpus'], gpu_total)}
        if hasattr(self, 'sch_obj') and self.sch_obj:
            requested_resources = {'gpus': (self.sch_obj.resources['gpus'], self.gpu_count)}
            try:
                self.sch_obj.reserve_resources(self, requested_resources)
            except Exception as e:
                self.sch_obj.task_error(self, e)
                self.log.write("Failed to allocate resource. \n")
                self.after_run()
                raise ValueError("Failed to allocate resource.")
            return True
        else:
            return False

    @override
    def after_run(self):
        if hasattr(self, '_hw_socketio_thread'):
            self._hw_socketio_thread.kill()

    @override
    def path(self, filename, relative=False):
        """
        Returns a path to the given file

        Arguments:
        filename -- the requested file

        Keyword arguments:
        relative -- If False, return an absolute path to the file
                    If True, return a path relative to the jobs directory
        """
        if not filename:
            return None
        if os.path.isabs(filename):
            path = filename
        else:
            path = os.path.join(self.job_dir, filename)
            if relative:
                path = os.path.relpath(path, config_value('jobs_dir'))
        return str(path).replace("\\", "/")

    @override
    def offer_resources(self, resources, locking_gpu=False):
        if locking_gpu:
            return None
        gpu_count = int(self.gpu_count) * (int(self.node_count))
        if 'gpus' not in resources:
            return None
        if not resources['gpus']:
            return {}  # don't use a GPU at all
        if gpu_count is not None:
            if resources['gpus'].remaining(label=self.node_label, value=gpu_count):
                return {'gpus': (resources['gpus'], int(gpu_count))}
        return None

    @override
    def task_arguments(self, resources, env, full_pod_name=None):
        args = [sys.executable,
                '--node_count=%d' % int(self.node_count),
                '--cpu_count=%d' % int(self.cpu_count),
                '--gpu_count=%d' % int(self.gpu_count),
                '--memory=%d' % int(self.memory),
                '--file_path=%s' % self.file_path,
                '--job_id=%s' % self.job_id,
                '--framework=%s' % self.framework,
                '--framework_version=%s' % self.framework_version,
                '--mount_path=%s' % self.mount_path,
                '--model_dir=%s' % self.model_dir,
                '--data_dir=%s' % self.data_dir,
                '--username=%s' % self.username,
                '--extra_parameter=%s' % self.extra_parameter,
                ]

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

        return args, resources_args

    def ready_to_queue(self):
        return True

    def run(self, resources, **kwargs):
        self.sch_obj = kwargs['sch_obj']
        full_pod_name = self.before_run()
        env = os.environ.copy()
        args, resources_args = self.task_arguments(resources, env, full_pod_name=full_pod_name)
        if not args:
            self.status = Status.ERROR
            return False
        self.status = Status.RUN
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if self.framework == "caffe" or self.framework == "tensorflow" or self.framework == "torch" or self.framework == "pytorch" or self.framework == "mxnet":
            args = ["kubectl logs -f %s" % (full_pod_name)]
            self.log.write("new_args:\n%s \n" % (' '.join(args)))
            print "new_args: %s" % (' '.join(args))
            self.p = subprocess.Popen(args=args,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT,
                                      cwd=base_dir,
                                      close_fds=False if platform.system() == 'Windows' else True,
                                      env=env,
                                      shell=True,
                                      )

        else:
            self.log.write("new_args:\n%s \n" % (' '.join(args)))
            print "* new_args: %s" % (' '.join(args))
            args = ' '.join(args)
            self.p = subprocess.Popen(args=args,
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
                        print("Touch Abort Enter")
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
                    self.log.write('Sent SIGKILL to task "%s"' % self.name())
                    time.sleep(0.1)
                time.sleep(0.01)
        except Exception as e:
            self.p.terminate()
            self.log.write("Def Run Exception : ", e)
            print "Def Run Exception : ", e
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
                      namespace='/jobs',
                      room=self.job_id,
                      )
        self.middle_run(line)
        data_line = self.regular_train_output(line)
        if not data_line:
            return 'No regular data line'
        if data_line:
            self.graph_data_txt.write('%s\n' % data_line)
            self.graph_data_txt.flush()
            socketio.emit('task update',
                          {
                              'task': 'vip_job',
                              'update': 'accuracy_graph',
                              'data': data_line,
                          },
                          namespace='/jobs',
                          room=self.job_id,
                          )

    def regular_train_output(self, line, cull=True):
        if self.framework == "torch":
            line_pattern = re.compile(r"{'(\w+)':\d+.\d+,'(\w+)':\d+.\d+,'(\w+)':\d+.\d+}")
        elif self.framework == "pytorch" or self.framework == "tensorflow":
            line_pattern = re.compile(r"{'(\w+)': \d+.\d+, '(\w+)': \d+.\d+, '(\w+)': \d+.\d+}")
        data_line = re.search(line_pattern, line)
        if data_line:
            data_line = eval(data_line.group())
            return data_line
        else:
            pass

    def judge_status(self):
        log_dir = os.path.join(config_value('jobs_dir'), self.job.username, 'jobs', str(self.job_id))
        single_log_path = os.path.join(log_dir, "au_%s_output.log" % (self.job.framework))
        if os.path.exists(str(single_log_path)):
            with open(str(single_log_path), 'r+') as file:
                file.seek(-250, 2)
                for line in file.readlines():
                    log_pattern = re.compile(r"Done|done")
                    regular_line = re.search(log_pattern, line)
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
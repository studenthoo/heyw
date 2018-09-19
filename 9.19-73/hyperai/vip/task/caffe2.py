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

# from hyperai.model.tasks.train import TrainTask
from hyperai import utils
from hyperai.webapp import socketio
from hyperai.task import Task
from hyperai.status import Status
from hyperai.utils import subclass, override
from collections import OrderedDict, namedtuple
from hyperai.tools.advanced_user.au_mpi_kuber_coordinate import KubernetasCoord
import gevent
import gevent.event
import time
from .train import TrainTask

class Caffe2:
    def __init__(self,name,mode):
        self.name = name
        self.mode = mode

    def create_train_task(self, **kwargs):
        return DistributedCaffe2Train(name=self.name,mode=self.mode, **kwargs)


@subclass
class DistributedCaffe2Train(TrainTask):
    """
    分布式训练任务
    """

    CAFFE2_LOG = 'au_caffe2_output.log'

    def __init__(self, **kwargs):
        # print "caffe2 single/distributed kwargs :" ,kwargs
        super(DistributedCaffe2Train, self).__init__(**kwargs)
        self.log_file = self.CAFFE2_LOG
        self.caffe2_log = None

    def __getstate__(self):
        state = super(DistributedCaffe2Train, self).__getstate__()

        if 'caffe2_log' in state:
            del state['caffe2_log']


        return state

    def __setstate__(self, state):
        super(DistributedCaffe2Train, self).__setstate__(state)



    def get_framework_id(self):
        """
        Returns a string
        """
        return self.framework_id

    @override
    def before_run(self):
        if self.mode == "single":
            self.caffe2_log = open(self.path(self.CAFFE2_LOG), 'a+')
            self.graph_data_txt = open(self.path(self.GRAPH_DATA_TXT), 'a+')

            self.args = ['python',
                         self.file_path,
                         '--data_dir=%s' % self.data_dir,
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

            try:
                kube_cood = KubernetasCoord(self.logger,
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
                return pod_name
            except Exception as e:
                raise IOError("Container Create Failed: %s" % e)

        else:
            self.au_worker_log = open(self.path(self.AU_WORKER_LOG), 'a+')
            self.graph_data_txt = open(self.path(self.GRAPH_DATA_TXT), 'a+')

    def middle_run(self,line):
        if self.mode == "single":
            self.caffe2_log.write('%s\n' % line)
            self.caffe2_log.flush()
        else:
            # print "self.au_worker_log: ",self.au_worker_log
            self.au_worker_log.write('%s\n' % line)
            self.au_worker_log.flush()

    @override
    def after_run(self):
        if self.mode == "single":
            KubernetasCoord.delete_pods(job_id=self.job_id)
            self.caffe2_log.close()
            self.graph_data_txt.close()
        else:
            self.au_worker_log.close()
            self.graph_data_txt.close()

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
            print("caffe2_distributed path: %s"%(path))
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
            if resources['gpus'].remaining():
                return {'gpus': (resources['gpus'], int(gpu_count))}
        return None

    @override
    def task_arguments(self, resources, env):
        if self.node_count >= 1:
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
                    '--data_dir=%s' % self.data_dir,
                    '--username=%s'%self.username,
                    '--extra_parameter=%s' % self.extra_parameter,
                    ]
        else:
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
        exe = args[0]
        new_path = os.path.join(os.path.dirname(os.path.abspath(hyperai.__file__)), 'tools', 'advanced_user',
                                'create_yaml.py')

        # new_args = [exe, str(new_path), "--argument=%s" % args[1:]]
        new_args = [exe, str(new_path)]
        back_args = args[1:]
        new_args.extend(back_args)

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

    def run(self, resources):

        full_pod_name = self.before_run()
        env = os.environ.copy()
        args, resources_args = self.task_arguments(resources, env)
        if not args:
            self.job.state = 2
            self.job.get_status()
            return False
        self.job.state = 1
        self.job.get_status()
        self.status = Status.RUN

        base_dir = os.path.dirname(os.path.abspath(__file__))

        sys.path.insert(0, os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

        base_dir = os.path.dirname(os.path.abspath(__file__))
        # print "base_dir: ", base_dir
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
                        print("Caffe2 Abort Enter")
                        if sigterm_time is None:
                            # Attempt graceful shutdown
                            self.p.send_signal(signal.SIGTERM)
                            sigterm_time = time.time()
                            self.job.state = 4
                            self.job.get_status()
                            self.status = Status.ABORT
                        break

                    if line is not None:
                        line = line.strip()
                    if line:
                        print line
                        time.sleep(0.1)
                        self.au_process_output(line)
                        sys.stdout.flush()

                if sigterm_time is not None and (time.time() - sigterm_time > sigterm_timeout):
                    self.p.send_signal(signal.SIGKILL)
                    self.logger.warning('Sent SIGKILL to task "%s"' % self.name())
                    time.sleep(0.1)
                time.sleep(0.01)

        except:
            self.p.terminate()
            self.after_run()
            raise

        self.job.state = 3
        self.job.get_status()
        self.after_run()

    def au_process_output(self,line):

        self.middle_run(line)

        data_line = self.regular_train_output(line)
        print "data_line: ",data_line
        if not data_line:
            return 'No regular data line'

        if data_line:
            print self.graph_data_txt
            self.graph_data_txt.write('%s\n' % data_line)
            self.graph_data_txt.flush()


            print "socketio line: ",data_line
            socketio.emit('task update',
                          {
                              'task': 'vip_job',
                              'update': 'accuracy_graph',
                              'data': data_line,
                          },
                          namespace='/jobs',
                          room=self.job_id,
                          )

    def regular_train_output(self,line,cull=True):

        line_pattern = re.compile(r"{'(\w+)': \d+.\d+, '(\w+)': \d+.\d+, '(\w+)': \d+.\d+}")
        data_line = re.search(line_pattern, line)
        if data_line:
            data_line = eval(data_line.group())
            print "regular line: ",data_line
            return data_line
        else:
            pass


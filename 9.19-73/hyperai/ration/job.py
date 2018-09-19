#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-2017, NVIDIA CORPORATION.  All rights reserved.

from hyperai.job import Job
import pickle
import os
import os.path
import time
import datetime
import shutil
import random
from hyperai.config import config_value

PICKLE_VERSION = 1
from hyperai.utils import subclass, override
from hyperai.tools.deploy.kube import KubernetasCoord as k8s
# from hyperai.webapp import scheduler


@subclass
class Deployment_job(Job):
    # 生成job对象拿取属性
    """docstring for deploy_job"""
    def __init__(self, username, **kwargs):
        # print kwargs

        # self._id = '%s-%s' % (time.strftime('%Y%m%d-%H%M%S'), os.urandom(2).encode('hex'))
        # self._dir = os.path.join(os.path.join(config_value('jobs_dir'), username + '/' + 'jobs' + '/' + self._id))
        # self.create_time = datetime.datetime.now()
        self.username = username
        self.number = None
        # self.status = 'Running'
        self.name = kwargs['name']
        self.model_desc = kwargs['model_desc'] # 描述
        self.gpu_count = kwargs['gpu_count']
        self.cpu_count = kwargs['cpu_count']
        self.memory = kwargs['memory_count']
        self.select_scence = kwargs['select_scence']  # 场景选择
        self.frame = kwargs['frame']
        # self.deployment_ways = kwargs['deployment_ways']  # 部署方式
        self.version = kwargs['version'] # 版本号
        self.optimization_engine = kwargs['optimization_engine']  # 优化引擎
        self.resources_deployment = kwargs['resources_deployment']  # 资源部署
        super(Deployment_job, self).__init__(name=self.name, username=self.username, desc=self.model_desc)
        self.tasks = []
        self.replicas = kwargs['replicas']
        self.job_status = ''
        self.nodePort = random.randint(30000, 32767)
        self.api_url = "http://{}:".format(config_value('deploy_ip'))+str(self.nodePort)
        self.api = self.api_url+'/api/classify'
        self.count_success = 0
        self.count_fail = 0
        self.scene = kwargs['scene']
        self.pic = kwargs['job_pic']
        self.flag = ''
        self.cpu = ''
        self.memory = ''
        self.mem = ''
        self.gpu = ''
        self.instance_max = 0
        if self.resources_deployment == '弹性伸缩模式':
            self.instance_min = int(kwargs['instance_min'])  # 最小值
            self.instance_max = int(kwargs['instance_max'])  # 最大值
    # def node_select(self):
    #     # node_list = []
    #     all_deployment_jobs = scheduler.get_deployment_jobs()
    #     for job in all_deployment_jobs:
    #         # node_list.append(job.nodePort)
    #         while self.nodePort == job.nodePort:
    #             self.nodePort = random.randint(30000, 32767)

    def id(self):
        """getter for _id"""
        return self._id

    def dir(self):
        """getter for _dir"""
        return self._dir

    def job_type(self):
        return 'deployment_job'

    @override
    def name(self):
        return self.name.encoding('utf-8')

    def train_task(self):
        """Return the first TrainTask for this job"""
        from hyperai.ration import task
        # print self.tasks
        return [t for t in self.tasks if isinstance(t, task.Task)][0]

    def get_status(self,job_id):
        output = k8s.short_exec_com()
        pod_list = k8s.parse_pod_msg(element=job_id,content=output)
        return pod_list
        # k8s.parse_pod_name(element=job_id,content=output)






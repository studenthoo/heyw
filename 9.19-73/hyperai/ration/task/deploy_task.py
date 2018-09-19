 #!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-2017, NVIDIA CORPORATION.  All rights reserved.
from __future__ import absolute_import
import os
import sys
import logging
import subprocess
import platform
import flask
import hyperai
import re
import gevent
import time
from hyperai.utils import subclass, override
from hyperai.task import Task
from hyperai.webapp import socketio,scheduler
from hyperai.status import Status
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from hyperai.tools.deploy.kube import KubernetasCoord
import gevent
import threading
from hyperai.config import config_value
from utils.resource_monitor2 import Monitor_Resource
from hyperai.ext import db
from hyperai.models import Monitor
from hyperai.webapp import app, socketio
from hyperai import utils
import signal
# from hyperai.ext import r

@subclass
class DeploymentTask(Task):
    # 生成yaml脚本的类
    """docstring for DeploymentTask"""
    deploymnet_log = 'deploymnet.log'

    def __init__(self, **kwargs):
        # print 'task start==========', kwargs
        self.job = kwargs['job']
        super(DeploymentTask, self).__init__(job_dir=self.job.dir())
        # self.job_dir = job.dir()
        # self.job_id = job.id()
        self.name = kwargs['name']
        self.gpu_count = kwargs['gpu_count']
        self.cpu_count = kwargs['cpu_count']
        self.memory = kwargs['memory_count']
        self.select_scence = kwargs['select_scence'] # 场景选择
        self.select_model = kwargs['select_model'] # 模型选择
        self.label_name = kwargs['label_name']
        # self.deployment_ways = kwargs['deployment_ways'] # 部署方式
        self.optimization_engine = kwargs['optimization_engine'] # 优化引擎
        self.resources_deployment = kwargs['resources_deployment'] # 资源部署
        self.image_tfserving = config_value('img_deploy_tfserving')
        self.image_tensorrt = config_value('img_deploy_tensorrt')
        self.nodePort = self.job.nodePort
        self.image = None
        self.command = None
        self.args = None
        self.set_logger()
        self.args = None
        self.yaml_path = None
        self.replicas = None
        self.pod_name_list = []
        self.average_number = 0
        self.total_number = 0
        self.total_memory = 0
        self.average_memory = 0
        self.gpu_list = []
        self.memory_list = []
        self.cpu_list = []
        self.mem_list = []
        self.mem_total = 0
        self.index = 0
        self.cpu_index = 0
        self.add_num = 0
        self.flag = "deployment_task"
        # self.status = Status.INIT
        if self.resources_deployment=='弹性伸缩模式':
            self.instance_min = int(kwargs['instance_min']) # 最小值
            self.instance_max = int(kwargs['instance_max']) # 最大值
            self.gpu_count_min = float(kwargs['gpu_count_min']) / 100
            self.gpu_count_max = float(kwargs['gpu_count_max']) / 100
        elif self.resources_deployment == '固定资源模式':
            self.replicas = kwargs['replicas']

    def __getstate__(self):
        state = super(DeploymentTask, self).__getstate__()

        # Don't pickle these things
        if 'labels' in state:
            del state['labels']
        if 'image_mean' in state:
            del state['image_mean']
        if 'classifier' in state:
            del state['classifier']
        if 'deploymnet_log' in state:
            del state['deploymnet_log']
        if '_hw_socketio_thread' in state:
            del state['_hw_socketio_thread']
        return state

    def __setstate__(self, state):
        super(DeploymentTask, self).__setstate__(state)
        # Make changes to self
        self.loaded_snapshot_file = None
        self.loaded_snapshot_epoch = None
        # These things don't get pickled
        self.image_mean = None
        self.classifier = None

    @override
    def before_run(self, optimization_engine, select_model):
        self.deploymnet_log = open(self.path(self.deploymnet_log), 'a+')

        if optimization_engine == 'TensorRT':
            self.command = ["sh", "-c"]
            args = ' '.join(['bash', select_model])
            self.args = [str(args)]
            self.image = self.image_tensorrt
        elif optimization_engine == 'TF-serving':
            self.image = self.image_tfserving
            self.args = ["cd /root/serving && bazel build -c opt //tensorflow_serving/model_servers:tensorflow_model_server && bazel-bin/tensorflow_serving/model_servers/tensorflow_model_server --port=9000 --model_name=mnist --model_base_path=/tmp/mnist_model/"]
        if self.resources_deployment == '弹性伸缩模式':
            replicas = self.instance_min
        elif self.resources_deployment == '固定资源模式':
            replicas = self.replicas
        try:
            kube_cood = KubernetasCoord(self.logger,
                                        job_id=self.job_id,
                                        job_dir=self.job_dir,
                                        gpu=self.gpu_count,
                                        cpu=self.cpu_count,
                                        memory=self.memory,
                                        image=self.image,
                                        args=self.args,
                                        optimization_engine=optimization_engine,
                                        command=self.command,
                                        replicas=replicas,
                                        nodePort=self.nodePort,
                                        label_name=self.label_name,
                                        )
            pod_name = kube_cood.container_prepare(self.job_id,optimization_engine) # 生成yaml脚本 并返回pod名字
            # print 'come in'
            # print 111, pod_name
            monitor = Monitor_Resource(self.job)
            self._hw_socketio_thread = gevent.spawn(monitor.hw_socketio_updater, self.job_id, self.resources_deployment)
            return pod_name

        except Exception as e:
            raise IOError("Container Create Failed: %s" % e)

    def middle_run(self, line):
        self.deploymnet_log.write('%s\n' % line)
        self.deploymnet_log.flush()

    @override
    def after_run(self):
        self.deploymnet_log.close()
        # if hasattr(self, '_hw_socketio_thread'):
        #     self._hw_socketio_thread.kill()

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
            # print("tf path: %s" % (path))
            if relative:
                path = os.path.relpath(path, config_value('jobs_dir'))
        return str(path).replace("\\", "/")

    @override
    def offer_resources(self, resources, locking_gpu=False):
        if locking_gpu:
            return None
        if self.resources_deployment == '弹性伸缩模式':
            gpu_count = int(self.gpu_count) * int(self.instance_min)
        elif self.resources_deployment == '固定资源模式':
            gpu_count = int(self.gpu_count) * (int(self.replicas))
        if 'gpus' not in resources:
            return None
        if not resources['gpus']:
            return {}  # don't use a GPU at all
        if gpu_count is not None:
            if resources['gpus'].remaining(value=gpu_count):
                return {'gpus': (resources['gpus'], int(gpu_count))}
        return None

    @override
    def task_arguments(self, resources, env):
        args = ['no need']
        new_args = args
        # 新返回的参数
        resources_args = {}
        if self.gpu_count:
            resources_args['gpu_count'] = self.gpu_count
        if self.cpu_count:
            resources_args['cpu_count'] = self.cpu_count
        if self.memory:
            resources_args['memory_count'] = self.memory
        if self.replicas:
            resources_args['replicas'] = self.replicas
        return new_args, resources_args

    def ready_to_queue(self):
        return True

    @override
    def run(self):
        full_pod_name = self.before_run(optimization_engine=self.optimization_engine, select_model=self.select_model)
        env = os.environ.copy()
        # args, resources_args = self.task_arguments(resources, env)
        self.status = Status.RUN
        # self.job.job_status = 'Running'
        base_dir = os.path.dirname(os.path.abspath(__file__))
        args = ["kubectl logs %s"%(full_pod_name)]
        # print "args: ", args
        time.sleep(8)
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
            # print '============>>', self.p.stdout.read(), self.p.poll(), self.p.stdout
            while self.p.poll() is None:
                for line in utils.nonblocking_readlines(self.p.stdout):
                    if self.aborted.is_set():
                        print("Tensorflow Abort Enter")
                        if sigterm_time is None:
                            # Attempt graceful shutdown
                            self.p.send_signal(signal.SIGTERM)
                            sigterm_time = time.time()
                            self.status = Status.ABORT
                        break
                    if line is not None:
                        line = line.strip()
                    if line:
                        # print 'line', line
                        self.middle_run(line)
                        sys.stdout.flush()
                    else:
                        time.sleep(0.05)
                if sigterm_time is not None and (time.time() - sigterm_time > sigterm_timeout):
                    self.p.send_signal(signal.SIGKILL)
                    self.logger.warning('Sent SIGKILL to task "%s"' % self.name())
                    time.sleep(0.1)
                time.sleep(0.01)
        except Exception as e:
            print 'error', e
            self.p.terminate()
        #     self.after_run()
        self.after_run()
        if self.resources_deployment == '弹性伸缩模式':

            def fun_timer():
                # print('Hello gpu!')
                global timer
                timer = threading.Timer(60, fun_timer)
                timer.start()
                self.deal_data()
                # print 'print self.job.job_status', self.job.job_status
                if self.job.job_status == 'Error':
                    timer.cancel()
            timer = threading.Timer(52, fun_timer)
            timer.start()

    def set_logger(self):
        self.logger = hyperai.log.JobIdLoggerAdapter(
            logging.getLogger('hyperai.webapp'),
            {'job_id': self.job_id},
        )

    def deal_data(self, timer=None):
        if 'ip' in os.environ:
            from hyperai.ext import influxdb_client
        self.memory_list = []
        self.gpu_list = []
        self.cpu_list = []
        self.mem_list = []
        self.pod_name_list = []
        a = 0
        with app.app_context():
            pod_name_list = self.job.get_status(self.job_id)
            if pod_name_list is None:
                pod_name_list = []
            for pod_list in pod_name_list:
                for index, pod_name in enumerate(pod_list):
                    if index == 0:
                        self.pod_name_list.append(pod_name)
            # print 'get pod list', self.pod_name_list
            if pod_name_list:
                # if self.memory_list or self.gpu_list:
                for pod_name in self.pod_name_list:
                    self.total_number = 0
                    self.total_memory = 0
                    try:
                        monitor = Monitor.query.filter_by(pod_name=pod_name).order_by(Monitor.create_time.desc()).limit(10).all()
                        # print 'get gpu count', monitor
                        for total in monitor:
                            # float(s.strip('%'))
                            self.total_number += (float(total.gpu_utilization.strip('%')) / 100)
                            self.total_memory += float(total.memory)
                            # print 'gpu_utilization', float(total.gpu_utilization.strip('%')), float(total.memory)
                        self.average_number = self.total_number / 10
                        self.average_memory = self.total_memory / 10
                        # print 'self.average_number', self.total_number, self.average_number, self.average_memory
                        self.gpu_list.append(float(self.average_number))
                        self.memory_list.append(float(self.average_memory))

                        # print self.gpu_count_max
                        # Monitor.query.filter_by(pod_name=pod_name).delete()
                    except Exception as e:
                        print e

                    try:
                        delete_data = Monitor.query.filter_by(pod_name=pod_name).all()
                        for i in delete_data:
                            db.session.delete(i)
                        db.session.commit()
                        sql = """select value from "cpu/usage_rate" where pod_name='%s' order by time desc limit 10""" % pod_name
                        # print 'sql', sql
                        result = influxdb_client.query(sql)
                        # print list(result)
                        for i in list(result):
                            self.index = len(i)
                            for j in i:
                                self.cpu_list.append(j['value'])

                        sql_two = """select value from "memory/usage" where pod_name='%s' order by time desc limit 10""" % pod_name
                        mem_used = influxdb_client.query(sql_two)
                        # print list(mem_used)
                        for i in list(mem_used):
                            self.cpu_index = len(i)
                            for j in i:
                                self.mem_list.append(j['value'])

                        sql_three = """select value from "memory/limit" where pod_name='%s' order by time desc limit 10""" % pod_name
                        mem_total = influxdb_client.query(sql_three)
                        # print list(mem_total)
                        for i in list(mem_total):
                            for j in i:
                                self.mem_total = j['value']
                    except Exception as e:
                        print e

                a = float(sum(self.gpu_list)) / float(len(self.gpu_list))
                deployment_name = "%s-%s" % (config_value('creater').encode('utf-8'), self.job_id)
                try:
                    if float(a) >= self.gpu_count_max:
                        if self.instance_min < self.instance_max:
                            self.instance_min = (self.instance_min + 1)
                            if scheduler.resources['gpus'].gpu_can_use >=1:
                                args = ["kubectl scale deployment %s --replicas=%d" % (
                                deployment_name.encode('utf-8'), self.instance_min)]
                                output = KubernetasCoord.short_exec_com(command=args)
                                # self.add_num =1
                                scheduler.ration_resources['gpus'].allocate(self, 1)
                                gpu_total = 1
                                # if r.get("{}_gpu".format(self.job.username)) is not None:
                                #     gpu_used = r.get("{}_gpu".format(self.job.username))
                                # else:
                                #     gpu_used = 0
                                #
                                # new_gpu_used = int(gpu_used) + gpu_total
                                # # print '---> add_1',new_gpu_used
                                # try:
                                #     r.set("{}_gpu".format(self.job.username), new_gpu_used)
                                # except Exception as e:
                                #     print e
                                #
                                # # print output
                            else:
                                print "Can't scale deployment because of no resoure cpu_can_use:{}".format(scheduler.ration_resources['gpus'].gpu_can_use)
                    elif float(a) <= self.gpu_count_min:
                        if self.instance_min > int(self.job.instance_min):
                            self.instance_min = (self.instance_min - 1)
                            args = ["kubectl scale deployment %s --replicas=%d" % (
                            deployment_name.encode('utf-8'), self.instance_min)]
                            output = KubernetasCoord.short_exec_com(command=args)
                            # self.add_num = 2
                            scheduler.ration_resources['gpus'].allocate(self, -1)
                            gpu_total = 1
                            # # print '++++++++++++++++++'
                            # if r.get("{}_gpu".format(self.job.username)) is not None:
                            #     gpu_used = r.get("{}_gpu".format(self.job.username))
                            # else:
                            #     gpu_used = 0
                            #
                            # new_gpu_used = int(gpu_used) - gpu_total
                            # # print 'desc_1',new_gpu_used
                            # if new_gpu_used < 0:
                            #     new_gpu_used = 0
                            # try:
                            #     r.set("{}_gpu".format(self.job.username), new_gpu_used)
                            # except Exception as e:
                            #     print e

                    if not self.index:
                        self.cpu_list = []
                        self.index = 1
                    if not self.cpu_index:
                        self.mem_list = []
                        self.cpu_index = 1
                        self.mem_total = 1

                    self.cpu_list = float(sum(self.cpu_list)) / float(self.index * 2)
                    self.mem_list = (float(sum(self.mem_list)) / float(self.cpu_index * 2)) / float(self.mem_total)

                    data = {}
                    if self.gpu_list:
                        data['gpu'] = round((sum(self.gpu_list) / len(self.gpu_list)), 4)
                    else:
                        data['gpu'] = 0
                    self.job.gpu = data['gpu']

                    if self.memory_list:
                        data['memory'] = round((sum(self.memory_list) / len(self.memory_list)), 4)
                    else:
                        data['memory'] = 0
                    self.job.memory = data['memory']

                    data['cpu'] = round((self.cpu_list/float(self.cpu_count*self.instance_min)) / 100, 4)
                    self.job.cpu = data['cpu']
                    data['men'] = round(self.mem_list, 4)
                    self.job.mem = data['men']
                    print '{}--{}'.format(self.job_id, data)
                    self.job.flag = 1
                    socketio.emit('gpu update',
                                  {
                                      'task': 'monitor',
                                      'update': 'gpu_utilization',
                                      'data': data,
                                  },
                                  namespace='/jobs',
                                  room=self.job.id(),
                                  )
                except Exception as e:
                    # print e
                    pass
            # else:
            #     if timer:
            #         timer.cancel()
            #     raise ValueError('container not found!')
            else:
                if timer:
                    timer.cancel()


    def relase_gpu_resoures(self):
        if self.resources_deployment == '弹性伸缩模式':
            num = self.instance_min
        elif self.resources_deployment == '固定资源模式':
            num = self.replicas
            scheduler.ration_resources['gpus'].gpu_can_use += int(num)
        if scheduler.resources['gpus'].gpu_can_use > config_value('ration_gpu'):
            scheduler.resources['gpus'].gpu_can_use = config_value('ration_gpu')

    # def relase_gpu_resoures_about_usr(self):
    #     username = self.job.username
    #     # gpu_num = 0
    #     if self.resources_deployment == '弹性伸缩模式':
    #         num = int(self.instance_min)
    #     elif self.resources_deployment == '固定资源模式':
    #         num = int(self.replicas)
    #     # print '-->release gpu user num',num
    #     gpu_used_old = r.get("{}_gpu".format(username))
    #     print ("\n* * [{id}] - release gpu about user: {name} {gpu_used}\n  ".format(id=self.job.id(), name=username,gpu_used=gpu_used_old))
    #     if gpu_used_old is not None:
    #         if (int(gpu_used_old) - num) >= 0:
    #             gpu_used_new = (int(gpu_used_old) - num)
    #         else:
    #             gpu_used_new = 0
    #         r.set("{}_gpu".format(username), gpu_used_new)
    #     else:
    #         r.set("{}_gpu".format(username), 0)
    #     pass

    # def release_res_about_user(self):
    #     if self.status not in (Status.DONE,):
    #         username = self.username
    #         gpu_num = 0
    #         for task in self.tasks:
    #             gpu_ = int(task.gpu_count) * int(task.node_count)
    #             gpu_num += gpu_
    #         gpu_used_old = r.get("{}_gpu".format(username))
    #         print ("\n* * [{id}] - release gpu about user: {name}\n  ".format(id=self.id(), name=self.username))
    #         if gpu_used_old is not None:
    #             gpu_used_new = (int(gpu_used_old) - gpu_num) if (int(gpu_used_old) - gpu_num) >= 0 else 0
    #             r.set("{}_gpu".format(username), gpu_used_new)
    #         else:
    #             r.set(username, 0)

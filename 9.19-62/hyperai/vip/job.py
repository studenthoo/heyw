#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-2017, NVIDIA CORPORATION.  All rights reserved.
from __future__ import absolute_import

from hyperai.job import Job
from hyperai.utils import subclass, override
import datetime
import os
import hyperai
import re
import pickle
import shutil
import time
from hyperai import utils
from hyperai.config import config_value
from hyperai.status import Status, StatusCls
from hyperai.ext import r


@subclass
class DistributedJob(Job):
    """
    a job that create distributed job
    """
    def __init__(self, mode, node_count, framework, cpu_count, main_name, **kwargs):
        self.flag = 'vip'
        self.mode = mode
        self.node_count = node_count
        self.state = None
        self.tasks = []
        self.job_status = 'Running'
        self.framework = framework
        self.clone = None
        self.cpu_count = cpu_count
        self.main_name = main_name
        super(DistributedJob, self).__init__(**kwargs)

    @override
    def job_type(self):
        return 'vip Job'

    def get_data(self):
        graph_data = []
        data_path = os.path.join(self._dir, 'au_graph_data.txt')
        if os.path.exists(data_path):
            with open(data_path, 'r+') as file_obj:
                for line in file_obj.readlines():
                    line = line.replace("\n", "")
                    line = eval(line)
                    graph_data.append(line)
            return graph_data

    def log_data(self):
        graph_data = []
        log_dir = os.path.join(config_value('jobs_dir'), self.username, 'jobs', str(self.id()))
        data_path = os.path.join(log_dir, "au_%s_output.log" % (self.framework))
        if os.path.exists(data_path):
            with open(data_path, 'r+') as file_obj:
                for line in file_obj.readlines():
                    line = line.replace("\n", "")
                    graph_data.append(line)
            return graph_data

    def runtime_of_tasks(self):
        """
        Returns the time (in sec) between when the first task started and when the last task stopped
        NOTE: this may not be what you're expecting if there was some WAIT time in-between
        """
        starts = []
        stops = []
        for task in self.tasks:
            for start_status, start_timestamp in task.status_history:
                if start_status == 'R':
                    starts.append(start_timestamp)
                    for stop_status, stop_timestamp in task.status_history:
                        if stop_status in ['D', 'A', 'E']:
                            stops.append(stop_timestamp)
                    break
        if len(starts):
            min_start = min(starts)
            if len(stops):
                max_stop = max(stops)
                return max_stop - min_start
            else:
                return time.time() - min_start
        else:
            return 0

    def train_task(self):
        """Return the first TrainTask for this job"""
        from hyperai.vip import task
        # print self.tasks
        return [t for t in self.tasks if isinstance(t, task.Task)][0]

    def release_res_about_user(self):
        username = self.username
        gpu_num = 0
        for task in self.tasks:
            gpu_ = int(task.gpu_count) * int(task.node_count)
            gpu_num += gpu_
        gpu_used_old = r.get("{}_gpu".format(username))
        if gpu_used_old is not None:
            gpu_used_new = (int(gpu_used_old) - gpu_num) if (int(gpu_used_old) - gpu_num) >= 0 else 0
            r.set("{}_gpu".format(username), gpu_used_new)
        else:
            r.set("{}_gpu".format(username), 0)
        self.tasks[0].logger.info("Release GPU: {username} - {num}\n".format(username=username, num=gpu_num))

    def formatSize(self, bytes):
        try:
            bytes = float(bytes)
            kb = round(bytes / 1024, 2)
        except:
            print("Invalid bytes format")
            return "Error"

        if kb >= 1024:
            M = round(kb / 1024, 2)
            if M >= 1024:
                G = round(M / 1024, 2)
                return "%.2fG" % (G)
            else:
                return "%.2fM" % (M)
        else:
            return "%.2fkb" % (kb)

    # 获取文件大小
    def getDocSize(self):
        try:
            username = utils.auth.get_username()
            log_dir = os.path.join(config_value('jobs_dir'), username, 'jobs', str(self.id()))
            log_name = "au_%s_output.log" % (self.framework)
            path = os.path.join(log_dir, log_name)
            if os.path.exists(str(path)):
                size = os.path.getsize(path)
                return self.formatSize(size)
            else:
                return ''
        except Exception as err:
            print(err)

    def abort(self):
        """
        Abort a job and stop all running tasks
        """
        if self.status not in ['D', 'E', ]:
            self.status = Status.ABORT
            for task in self.tasks:
                task.abort()

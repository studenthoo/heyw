# Copyright (c) 2014-2017, NVIDIA CORPORATION.  All rights reserved.
from __future__ import absolute_import

from hyperai.job import Job
from hyperai.utils import subclass, override
import os
import os.path
import time
import re
from datetime import datetime
from hyperai import utils
from hyperai.config import config_value
from hyperai.status import Status, StatusCls
# from hyperai.ext import r

@subclass
class ParaJob(Job):

    def __init__(self, framework, cpu_count, server_path, **kwargs):
        self.begin_time = datetime.now()
        self.end_time = ''
        self.cost_time = ''
        self.cost_time = ''
        self.method = ''
        self.lr = ''
        self.momentum = ''
        self.decay = ''
        self.beta1 = ''
        self.beta2 = ''
        # self.status = ''
        self.train_lr = ''
        self.train_momentum = ''
        self.train_decay = ''
        self.train_beta1 = ''
        self.train_beta2 = ''
        self.number = None
        self.state = None
        self.tasks = []
        self.framework = framework
        self.cpu_count = cpu_count
        self.server_path = server_path
        super(ParaJob, self).__init__(**kwargs)

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
        else:
            return None
    @override
    def job_type(self):
        return 'Para Job'

    def train_task(self):
        """Return the first TrainTask for this job"""
        from hyperai.tuning import task
        return [t for t in self.tasks if isinstance(t, task.Task)][0]

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

    def getDocSize(self):
        try:
            username = utils.auth.get_username()
            log_dir = os.path.join(config_value('jobs_dir'), username, 'jobs', str(self.id()))
            log_name = 'au_ParaOPT_output.log'
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
        # if self.status.is_running():

        if self.status not in ['D', 'E']:
            self.status = Status.ABORT
            for task in self.tasks:
                task.abort()
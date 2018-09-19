# !/usr/bin/python
# -*- coding:utf-8 -*-
from __future__ import absolute_import

from collections import OrderedDict
import os
import sys
import shutil
import signal
import time
import traceback
import logging
import threading
import subprocess
import re
import gevent
import gevent.event
import gevent.queue
import json
from .ext import r
from .vip import DistributedJob
from . import utils
from hyperai.config import config_value
from .job import Job
from .log import logger
from .status import Status
from hyperai.utils import errors
from hyperai.queue import PriorityQueue, JobQueue
import threading
from .tuning import ParaJob
from hyperai.tools.advanced_user.au_mpi_kuber_coordinate import KubernetasCoord as k8s
from collections import defaultdict
from hyperai.users import register_user

"""
This constant configures how long to wait before automatically
deleting completed non-persistent jobs
"""
NON_PERSISTENT_JOB_DELETE_TIMEOUT_SECONDS = 3600


class Resource(object):
    """
    Stores information about which tasks are using a resource
    """

    class ResourceAllocation(object):
        """
        Marks that a task is using [part of] a resource
        """

        def __init__(self, task, value):
            """
            Arguments:
            task -- which task is using the resource
            value -- how much of the resource is being used
            """
            self.task = task
            self.value = value

    def __init__(self, identifier=None, max_value=1):
        """
        Keyword arguments:
        identifier -- some way to identify this resource
        max_value -- a numeric representation of the capacity of this resource
        """
        if identifier is None:
            self.identifier = id(self)
        else:
            self.identifier = identifier
        self.max_value = max_value
        self.allocations = []

    def remaining(self):
        """
        Returns the amount of this resource that is not being used
        """
        return 2

    def allocate(self, task, value):
        """
        A task is requesting to use this resource
        """
        if self.remaining() - value < 0:
            task.log.write('Resource is already maxed out at %s/%s' % (
                self.remaining(),
                self.max_value))
            raise RuntimeError('Resource is already maxed out at %s/%s' % (
                self.remaining(),
                self.max_value)
                               )
        self.allocations.append(self.ResourceAllocation(task, value))

    def deallocate(self, task):
        """
        The task has finished using this resource
        """
        for i, a in enumerate(self.allocations):
            if id(task) == id(a.task):
                self.allocations.pop(i)
                return True
        return False


class GpuResource(object):
    """"""
    class ResourceAllocation(object):
        """
        Marks that a task is using [part of] a resource
        """

        def __init__(self, task, value, label):
            """
            Arguments:
            task -- which task is using the resource
            value -- how much of the resource is being used
            """
            self.task = task
            self.value = value
            self.label = label
    def __init__(self, gpu_max, label_list, cpu_list, memory_list):
        """label_list=[(label01, 2), (label02, 2), (label03, 2), ]
            cpu_list=[{u'GTX-1080TI': 64}, {u'GTX-1060': 96}]
            memory_list=[{u'GTX-1080TI': 250}, {u'GTX-1060': 502}]
        """
        self.resource_dict = {}
        for item in label_list:
            if item not in self.resource_dict:
                self.resource_dict[item[0]] = [item[1]]
            else:
                print "传值错误..."
                raise ValueError('传值错误')
        for c in cpu_list:
            for k,v in c.items():
                if k in self.resource_dict:
                    self.resource_dict[k].append(v)
                else:
                    print "error"
                    raise ValueError('传值错误')

        for m in memory_list:
            for k, v in m.items():
                if k in self.resource_dict:
                    self.resource_dict[k].append(v)
                else:
                    print "error"
                    raise ValueError('传值错误')



        print self.resource_dict
        #resource_dict = {'GTX-1080TI': [4, 64, 250], 'GTX-1060': [4, 96, 502]}
        self._gpu_max = gpu_max if gpu_max else sum([i[-1] for i in label_list])
        self.gpu_can_use = self._gpu_max
        self.allocations = []
        # self.label_init_dict = {i[0]: [i[1],] for i in label_list}

        self.label_dict = {k: [int(v[0]), int(v[0]), int(v[1]), int(v[1]), int(v[2]), int(v[2])] for k, v in self.resource_dict.items()  }
        #label_dict = {'GTX-1080TI': [4, 4, 64, 64, 250, 250], 'GTX-1060': [4, 4, 96, 96, 502, 502]}

    def get_gpu_max(self):
        return self._gpu_max

    def get_used_label_gpu(self):
        return {k: v[0] - v[1] for k, v in self.label_dict.items()}

    def get_usable_label_gpu(self):
        one_dict = {k: [v[1],v[3],v[5]] for k, v in self.label_dict.items()}
        temp_dict = {}
        # print one_dict
        for k, v in one_dict.items():
            # c =[]
            for index,i in enumerate(v):
                # print "123",index
                # print "234",i
                if i < 0:
                    # temp_dict[k] = 0
                    v[index] = 0
                else:
                    # temp_dict[k] = v
                    v[index]=i
            temp_dict[k] = v
        # print temp_dict
        return temp_dict
        # temp_dict = {'GTX-1080TI': [4, 64, 250], 'GTX-1060': [4, 96, 502]}

    def get_usable_label_all(self):
        one_dict = {k: v for k, v in self.label_dict.items()}
        temp_dict = {}
        print one_dict
        for k, v in one_dict.items():
            gpu_list =[]
            cpu_list = []
            memory_list = []
            all_list = []
            for index,i in enumerate(v):
                # print "123",index
                # print "234",i
                if index == 0 or index ==1:
                    if i < 0:
                        # temp_dict[k] = 0
                        v[index] = 0
                    else:
                        # temp_dict[k] = v
                        v[index] = i
                    gpu_list.append(v[index])
                elif index == 2 or index ==3:
                    if i < 0:
                        # temp_dict[k] = 0
                        v[index] = 0
                    else:
                        # temp_dict[k] = v
                        v[index] = i
                    cpu_list.append(v[index])
                elif index == 4 or index == 5:
                    if i < 0:
                        # temp_dict[k] = 0
                        v[index] = 0
                    else:
                        # temp_dict[k] = v
                        v[index] = i
                    memory_list.append(v[index])
            all_list.append(gpu_list)
            all_list.append(cpu_list)
            all_list.append(memory_list)
            #     if i < 0:
            #         # temp_dict[k] = 0
            #         v[index] = 0
            #     else:
            #         # temp_dict[k] = v
            #         v[index]=i
            temp_dict[k] = all_list
        return temp_dict

    def get_gpu_used(self):
        return self._gpu_max - self.gpu_can_use

    def change_gpu_count(self, gpu_max):
        # change the count of all gpus
        if gpu_max:
            self._gpu_max = gpu_max
        pass

    def allocate(self, task, value):
        print value
        print task.cpu_count
        print task.memory
        value = int(value)
        cpu_count = int(task.cpu_count)
        memory = int(task.memory)
        """
        if self.gpu_can_use - value < 0:
            print('< System > Resource is already maxed out %s/%s.' % (value, self.gpu_can_use))
            raise RuntimeError("Resource.")
            # return False
        usable_label_gpu = self.get_usable_label_gpu()
        if usable_label_gpu[task.node_label] - value < 0:
            print('< Resources Pool: %s > Resource is already maxed out %s/%s.' % (
            task.node_label, value, usable_label_gpu[task.node_label]))
            raise RuntimeError("Resource.")
            # return False
        """
        if self.allocations:
            # self.allocations = [[task, value, label], [task, value, label]]
            for each in self.allocations:
                if id(each[0]) == id(task):
                    each[1] += value
                    self.gpu_can_use = self.gpu_can_use - value
                    self.label_dict[task.node_label][1] -= value
                    self.label_dict[task.node_label][3] -= cpu_count
                    self.label_dict[task.node_label][5] -= memory
                    task.logger.info(
                        "< System > < Resources Pool:  %s > Allocate the resources Successed . GPU=[%d]" % (
                        task.node_label, value))
                    return True
            # for each in self.allocations:
            #     if id(each.task) == id(task):
            #         each.value += value
            #         self.gpu_can_use = self.gpu_can_use - value
            #         self.label_dict[task.node_label][1] -= value
            #         task.logger.info(
            #             "< System > < Resources Pool - %s > Allocate the resources Successed . GPU=[%d] label_dict=%s" % (
            #             task.node_label, value, self.label_dict))
            #         return True
        self.gpu_can_use = self.gpu_can_use - value
        self.label_dict[task.node_label][1] -= value
        self.label_dict[task.node_label][3] -= cpu_count
        self.label_dict[task.node_label][5] -= memory
        print self.label_dict[task.node_label][1]
        print self.label_dict
        self.allocations.append([task, value, task.node_label])
        # self.allocations.append(self.ResourceAllocation(task, value, task.node_label))
        task.logger.info("< System > < Resources Pool: %s > Allocate the resources Successed . GPU=[%d]" % (
            task.node_label, value))
        return True

    def deallocate(self, task):
        """
        The task has finished using this resource
        """
        # self.allocations = [[task, value, label], [task, value, label]]
        print "123",self.allocations
        for i, a in enumerate(self.allocations):
            if id(task) == id(a[0]):
                self.gpu_can_use = self.gpu_can_use + a[1]
                self.label_dict[a[0].node_label][1] += a[1]
                self.label_dict[a[0].node_label][3] += int(a[0].cpu_count)
                self.label_dict[a[0].node_label][5] += int(a[0].memory)
                self.allocations.pop(i)
                # task.logger.info("Deallocate the resources Successed . GPU=[%d]" % a.value)
                task.logger.info("< System > < Resources Pool: [%s] > Deallocate the resources Successed . GPU=[%d], CPU=[%d], memory=[%d]" % (task.node_label, a[1], int(task.cpu_count), int(task.memory)))
                return True
        # for i, a in enumerate(self.allocations):
        #     if id(task) == id(a.task):
        #         self.gpu_can_use = self.gpu_can_use + a.value
        #         self.label_dict[a.task.node_label][1] += a.value
        #         self.allocations.pop(i)
        #         # task.logger.info("Deallocate the resources Successed . GPU=[%d]" % a.value)
        #         task.logger.info(
        #             "< System > < Resources Pool [%s] > Deallocate the resources Successed . GPU=[%d] label_dict=%s" % (
        #             task.node_label, a.value, self.label_dict))
        #         return True
        task.logger.info("Deallocate the resources Failed .Because not found this task in form of resources items.")
        return False

    def remaining(self, value=0, label=None, look_gpu=False):
        """
        Without judgment, all will pass.
        Returns the amount of this resource that is not being used
        """
        # if self.gpu_can_use - value < 0:
        #         #     return False
        #         # return self.gpu_can_use
        if look_gpu:
            return self.gpu_can_use if self.gpu_can_use >= 0 else sum(
                [v for k, v in self.get_usable_label_gpu().items()])
        return self.gpu_can_use


def read_gpu_count():
    # path = os.path.join(config_value('public_dir'), 'gpu1.txt')
    path = '/root/hyperai/deploy_gpu.txt'
    if os.path.exists(path):
        with open(path, 'r+') as f:
            a = f.read()
            print a
            b = json.loads(a)
            num = 0
            for i, p in b.items():
                r.set('{}_gpu'.format(i), p)
                num += int(p)
            gpu_used = int(num)
    else:
        gpu_used = 0
    return gpu_used


cons_gpu_max = config_value('gpus_init_cluster')
resources_label = config_value('resources_label')

if 'ip' in os.environ:
    from hyperai.ext import influxdb_client
sql = """select distinct(nodename) from "gpu/usage_rate1" """
result = influxdb_client.query(sql)
cpu_list = []
memory_list = []
for i in list(result):
    for j in i:
        node_sql = """select * from "gpu/usage_rate1" where nodename='%s' order by time desc limit 1""" % (j['distinct'])
        # print node_sql
        node_result = influxdb_client.query(node_sql)
        # print node_result
        for k in list(node_result):
            # print k
            cpu_dict = {}
            memory_dict = {}
            cpu_core = k[0]['cpu_logiccore']
            node = j['distinct']
            memory_free = int(k[0]['memory_total_cpu'])
            args = ['kubectl get nodes --show-labels | grep '+node+'| cut -d "," -f 3 | cut -d "=" -f 2']
            output = k8s.short_exec_com(command=args)
            if output:
                output = output.splitlines()
                cpu_dict[output[0]] = cpu_core
                memory_dict[output[0]] = memory_free
                cpu_list.append(cpu_dict)
                memory_list.append(memory_dict)
# print node_list
cpu_dic = {}
for i in cpu_list:
    for k, v in i.items():
        cpu_dic.setdefault(k, []).append(v)
cpu_result = [{k:v} for k, v in cpu_dic.items()]
# print result
new_cpu_list = []
for re in cpu_result:
    dict = {}
    for key,value in re.items():
        sum = 0
        for i in value:
            sum +=i
        dict[key] = sum
    new_cpu_list.append(dict)
print new_cpu_list

memory_dic = {}
for i in memory_list:
    for k, v in i.items():
        memory_dic.setdefault(k, []).append(v)
memory_result = [{k:v} for k, v in memory_dic.items()]
# print result
new_memory_list = []
for re in memory_result:
    dict = {}
    for key,value in re.items():
        sum = 0
        for i in value:
            sum +=i
        dict[key] = sum
    new_memory_list.append(dict)
print new_memory_list



class Scheduler:
    """
    Coordinates execution of Jobs
    """

    def __init__(self, gpu_list=None, verbose=False):
        """
        Keyword arguments:
        gpu_list -- a comma-separated string which is a list of GPU id's
        verbose -- if True, print more errors
        """
        self.verbose = verbose

        # Keeps track of resource usage
        num = read_gpu_count()
        self.resources = {
            'parse_folder_task_pool': [Resource()],
            'create_db_task_pool': [Resource(max_value=4)],
            'analyze_db_task_pool': [Resource(max_value=4)],
            'inference_task_pool': [Resource(max_value=4)],
            'extract_dataset_file_pool': [Resource(max_value=4)],
            'gpus_infer': [Resource(identifier=index)
                           for index in gpu_list.split(',')] if gpu_list else [],
            'gpus': GpuResource(gpu_max=cons_gpu_max, label_list=resources_label, cpu_list=new_cpu_list, memory_list=new_memory_list),
        }
        print 333
        # print "label_list=", resources_label
        print 222
        self.resources['gpus'].gpu_can_use = cons_gpu_max - int(num)
        self.running = False
        self.shutdown = gevent.event.Event()

        # create the Queues
        self.pending_jobs = PriorityQueue()
        self.running_jobs = JobQueue()
        self.other_jobs = JobQueue()

        # ======= log ===========
        self.mylog = logging.getLogger("Scheduler")
        _h = logging.FileHandler("/root/sed.log")
        _h.setFormatter(logging.Formatter("%(asctime)s %(name)s [%(levelname)s]: %(message)s"))
        self.mylog.addHandler(_h)
        self.mylog.setLevel(logging.INFO)
        self.mylog.info("======================================================")
        self.mylog.info("Scheduler started!")
        self.status_update = True
        print 11111

    def get_jobs(self, job_id=None):
        """ get all jobs whether status """
        jobs = self.running_jobs.get_jobs() + self.pending_jobs.get_jobs() + self.other_jobs.get_jobs()
        if job_id:
            for job in jobs:
                if job.id() == job_id:
                    return job
                else:
                    return None
        return jobs

    def abort_running_jobs(self, username):
        """ get all jobs whether status """
        all_jobs = self.get_jobs()
        running_jobs = [job for job in all_jobs if
                           job.status not in ['D', 'E', 'A'] and job.username == username]
        for job in running_jobs:

            if self.abort_job(job.id()):
                pass
            else:
                raise werkzeug.exceptions.Forbidden('Job not aborted')
                return False
        return True

    def load_past_jobs_scheduler(self):
        loaded_jobs = []
        failed_jobs = []
        alljobs_path = os.path.join(config_value('jobs_dir'), "alljobs")
        for dir_name in sorted(os.listdir(alljobs_path)):
            if os.path.isdir(os.path.join(alljobs_path, dir_name)):
                if dir_name in self.get_jobs():
                    continue
                try:
                    job = Job.load(path=os.path.join(alljobs_path, dir_name))
                    # The server might have crashed
                    if isinstance(job, DistributedJob):
                        if job.status not in ['D', 'E']:
                            job.status = Status.ABORT

                    elif isinstance(job, ParaJob):
                        if job.status not in ['D', 'E']:
                            job.status = Status.ABORT

                    elif job.status.is_running():
                        job.status = Status.ABORT

                    for task in job.tasks:
                        if task.status.is_running():
                            task.status = Status.ABORT

                    # We might have changed some attributes here or in __setstate__
                    job.save()
                    loaded_jobs.append(job)
                except Exception as e:
                    failed_jobs.append((dir_name, e))

        # add DatasetJobs or PretrainedModelJobs
        for job in loaded_jobs:
            if isinstance(job, DistributedJob):
                try:
                    self.other_jobs.put(job)
                except Exception as e:
                    failed_jobs.append((dir_name, e))

        for job in loaded_jobs:
            if isinstance(job, ParaJob):
                try:
                    self.other_jobs.put(job)
                except Exception as e:
                    failed_jobs.append((dir_name, e))
        logger.info('Loaded %d jobs.' % self.other_jobs.length())

        if len(failed_jobs):
            logger.warning('Failed to load %d jobs.' % len(failed_jobs))
            if self.verbose:
                for job_id, e in failed_jobs:
                    logger.debug('%s - %s: %s' % (job_id, type(e).__name__, str(e)))
        pass

    def add_job(self, job):
        """
        Add a job to self.Pending
        """
        if not self.running:
            logger.error('Scheduler not running. Cannot add job.')
            return False
        else:
            self.pending_jobs.put(job)
            self.status_update = True
            return True

    def get_job(self, job_id):
        if job_id is None:
            return None
        if self.other_jobs.get_by_job_id(job_id):
            return self.other_jobs.get_by_job_id(job_id)
        elif self.pending_jobs.get_by_job_id(job_id):
            return self.pending_jobs.get_by_job_id(job_id)

        elif self.running_jobs.get_by_job_id(job_id):
            return self.running_jobs.get_by_job_id(job_id)
        else:
            pass

    def get_related_jobs(self, job):
        related_jobs = []
        jobs = self.get_jobs()
        # if isinstance(job, ModelJob):
        #     datajob = job.dataset
        #     related_jobs.append(datajob)
        # elif isinstance(job, DatasetJob):
        #     datajob = job
        if isinstance(job, DistributedJob):
            datajob = job
        elif isinstance(job, ParaJob):
            datajob = job
        else:
            raise ValueError("Unhandled job type %s" % job.job_type())

        # for j in jobs:
        #     if isinstance(j, ModelJob):
        #         if datajob == j.train_task().dataset and j.id() != job.id():
        #             related_jobs.append(j)

        return related_jobs

    def abort_job(self, job_id):
        """
        Aborts a running Job
        Returns True if the job was found and aborted
        """
        job = self.get_job(job_id)

        if job is None or not job.status.is_running():
            return False
        job.abort()
        logger.info('Job aborted.', job_id=job_id)
        self.mylog.info("Abort job: %s", str(job_id))
        return True

    def delete_job(self, job):
        """job: job_id or Job """
        if isinstance(job, str) or isinstance(job, unicode):
            job_id = str(job)
        elif isinstance(job, Job):
            job_id = job.id()
        else:
            raise ValueError('called delete_job with a %s' % type(job))
        dependent_jobs = []
        path = os.path.join(config_value("jobs_dir"), "alljobs")
        job = self.get_job(job_id)
        if job:
            job.abort()
            if os.path.exists(job.dir()):
                try:
                    os.remove(os.path.join(path, job_id))
                except Exception as e:
                    print e

            if self.other_jobs.remove_by_job_id(job_id):
                pass
            if self.pending_jobs.remove_by_job_id(job_id):
                pass
            if self.running_jobs.remove_by_job_id(job_id):
                pass

            logger.info('Job deleted.', job_id=job.id())
            from hyperai.webapp import socketio
            socketio.emit('job update',
                          {
                              'update': 'deleted',
                              'job_id': job.id()
                          },
                          namespace='/jobs',
                          room='job_management',
                          )
            print "* [{job_id}] Delete Successed .".format(job_id=job.id())
            return True

        # see if the folder exists on disk
        path = os.path.join(config_value('jobs_dir'), job_id)
        path = os.path.normpath(path)
        if os.path.dirname(path) == config_value('jobs_dir') and os.path.exists(path):
            shutil.rmtree(path)
            return True
        return False

    def running_dataset_jobs(self):
        """a query utility"""
        # TODO
        return sorted(
            [j for j in self.jobs.values() if isinstance(j, DatasetJob) and j.status.is_running()],
            cmp=lambda x, y: cmp(y.id(), x.id())
        )

    def completed_dataset_jobs(self):
        """a query utility"""
        return sorted(
            [j for j in self.get_jobs() if isinstance(j, DatasetJob) and not j.status.is_running()],
            cmp=lambda x, y: cmp(y.id(), x.id())
        )

    # def running_model_jobs(self):
    #     """a query utility"""
    #     return sorted(
    #         [j for j in self.get_jobs() if isinstance(j, ModelJob) and j.status.is_running()],
    #         cmp=lambda x, y: cmp(y.id(), x.id())
    #     )
    #
    # def completed_model_jobs(self):
    #     """a query utility"""
    #     return sorted(
    #         [j for j in self.get_jobs() if isinstance(j, ModelJob) and not j.status.is_running()],
    #         cmp=lambda x, y: cmp(y.id(), x.id())
    #     )
    #
    # def print_status(self):
    #     model_job_count = self.running_jobs.len_by_class(ModelJob)
    #     normal_job_count = self.running_jobs.length() - model_job_count
    #     self.mylog.info("Scheduler status: %d Running normal jobs, %d Running model jobs,"
    #                     "%d Pending jobs, %d other jobs, %d GPU free!",
    #                     normal_job_count, model_job_count, self.pending_jobs.length(), self.other_jobs.length(),
    #                     self.resources["gpus"].remaining())

    def start(self):
        """
        Start the Scheduler
        Returns True on success
        """
        if self.running:
            return True

        gevent.spawn(self.main_thread)

        self.running = True
        return True

    def stop(self):
        """
        Stop the Scheduler
        Returns True if the shutdown was graceful
        """
        self.shutdown.set()
        wait_limit = 5
        start = time.time()
        while self.running:
            if time.time() - start > wait_limit:
                return False
            time.sleep(0.1)
        return True

    def main_thread(self):
        from hyperai import handleProf
        handleProf.register()

        signal.signal(signal.SIGTERM, self.sigterm_handler)
        signal.signal(signal.SIGUSR1, self.siguser_handler)
        try:
            last_saved = None
            print("Scheduler Start ...")
            i = 0
            while not self.shutdown.is_set():
                count_running_start = self.running_jobs.length()
                count_free_gpu_start = self.resources['gpus'].remaining()
                task_started = 0

                # running queue
                job_done_list = []
                for job in self.running_jobs.get_jobs():
                    all_done = True
                    for task in job.tasks:
                        if task.status in (Status.DONE,):
                            pass
                        elif task.status in (Status.ABORT,):
                            print("* < SCH >  TASK ABORT ..........................")
                            all_done = False
                            job.status = Status.ABORT
                            task.logger.info("* < SCH > Job is aborted.")
                            job_done_list.append(job)
                            break
                        elif task.status in (Status.ERROR,):
                            print("* < SCH >  TASK ERROR ..........................")
                            all_done = False
                            job.abort_other_task()
                            job.status = Status.ERROR
                            task.logger.info("* < SCH > Job is error. ")
                            job_done_list.append(job)
                            break
                        elif task.status in (Status.INIT, Status.WAIT):
                            all_done = False
                            if id(task) == id(job.get_first_task()):
                                job.status = Status.WAIT
                                continue
                            if task.ready_to_queue():
                                requested_resources = task.offer_resources(self.resources)
                                if requested_resources is None:
                                    task.status = Status.WAIT
                                else:
                                    if self.reserve_resources(task, requested_resources):
                                        gevent.spawn(self.run_task, task, requested_resources)
                                        task.status = Status.RUN
                                        self.status_update = True
                                        # task_started += 1
                        elif task.status in (Status.RUN,):
                            all_done = False
                            job.status = Status.RUN
                        else:
                            pass
                    if all_done:
                        job.status = Status.DONE
                        self.mylog.info("Job is done: %s", str(job.id()))
                        job_done_list.append(job)
                        logger.info('Job complete.', job_id=job.id())
                        job.save()
                for job in job_done_list:
                    self.running_jobs.remove_by_job_id(job.id())
                    self.other_jobs.put(job)
                    # job.release_res_about_user()
                    if isinstance(job, (ParaJob, DistributedJob)):
                        for task in job.tasks:
                            register_user.deallocate_resources(job.username, task)
                    self.mylog.info("Job move to other: %s", str(job.id()))

                # pending queue
                move_to_running_list = []
                move_to_other_list = []
                start_index = self.pending_jobs.length()
                if start_index:
                    for i in range(1, start_index + 1):
                        job = self.pending_jobs.get_by_index(index=-i)
                        if job.status in [Status.DONE, Status.ERROR, Status.ABORT]:
                            move_to_other_list.append(job)
                            continue

                        def depend_judge(job):
                            return True

                        if depend_judge(job):
                            task = job.get_first_task()
                            if task and task.ready_to_queue():
                                if i == 1:
                                    requested_resources = task.offer_resources(self.resources, locking_gpu=False)
                                else:
                                    requested_resources = task.offer_resources(self.resources, locking_gpu=True)
                                if requested_resources is None:
                                    # not enough resources
                                    job.status = Status.WAIT
                                    for task in job.tasks:
                                        task.status = Status.WAIT
                                else:
                                    if isinstance(job, (DistributedJob, ParaJob)) or self.reserve_resources(task, requested_resources):
                                        gevent.spawn(self.run_task, task, requested_resources)
                                        move_to_running_list.append(job)
                        else:
                            pass
                    for job in move_to_running_list:
                        self.pending_jobs.remove_by_job_id(job.id())
                        self.mylog.info("Job from pending move to running: %s", str(job.id()))
                        self.running_jobs.put(job)
                    for job in move_to_other_list:
                        self.pending_jobs.remove_by_job_id(job.id())
                        self.other_jobs.put(job)
                        # job.release_res_about_user()
                        if isinstance(job, (ParaJob, DistributedJob)):
                            for task in job.tasks:
                                register_user.deallocate_resources(job.username, task)
                        self.mylog.info("Job from pending move to other: %s", str(job.id()))
                pass
                # save running jobs every 15 seconds
                if not last_saved or time.time() - last_saved > 15:
                    for job in self.get_jobs():
                        if job.status.is_running():
                            if job.is_persistent():
                                job.save()
                        elif (not job.is_persistent()
                              and (time.time() - job.status_history[-1][1] >
                                   NON_PERSISTENT_JOB_DELETE_TIMEOUT_SECONDS)):
                            # job has been unclaimed for far too long => proceed to garbage collection
                            self.delete_job(job)
                    last_saved = time.time()

                if 'HYPERAI_MODE_TEST' not in os.environ:
                    # time.sleep(utils.wait_time())
                    self.mylog.info("* * [Scheduler] * * loop [{count}] * * Thread Count [{num}] ."
                                    .format(count=i, num=threading.active_count()))
                    s_time = time.time()
                    self.mylog.info("* * [Scheduler] * * loop [{count}] * * [{time}] * * ".format(count=i, time="%.4f" % (time.time(),)))
                    # gevent.sleep(0.3)
                    time.sleep(0.3)
                    self.mylog.info("* * [Scheduler] * * loop [{count}] * * [{time}] * * ".format(count=i, time="%.4f" % (time.time(),)))
                    self.mylog.info("* * [Scheduler] * * loop [{count}] * * [{time}] * * \n".format(count=i, time="%.4f" % (time.time()-s_time)))
                    i += 1
                else:
                    gevent.sleep(0.3)
        except KeyboardInterrupt:
            pass
        print "Systerm killed ..."
        for job in self.get_jobs():
            job.abort()
            job.save()
        self.running = False

    def sigterm_handler(self, signal, frame):
        """
        Catch SIGTERM in addition to SIGINT
        """
        self.shutdown.set()

    def siguser_handler(self, signal, frame):
        self.status_update = True

    def task_error(self, task, error):
        """
        Handle an error while executing a task
        """
        try:
            task.log.write('%s: %s jobid=%s' % (type(error).__name__, error, task.job_id))
        except Exception as e:
            pass
        logger.error('%s: %s' % (type(error).__name__, error), job_id=task.job_id)
        self.mylog.error("Task of %s error: %s", str(task.job_id), error)
        task.exception = error
        task.traceback = traceback.format_exc()
        task.status = Status.ERROR

    def reserve_resources(self, task, resources):  # resources={'gpus': (resource_obj, self.gpu_count)}
        try:
            # if self.get_pod_msg_poll(task):
            for resource_type, requests in resources.iteritems():
                if resource_type == "gpus":
                    requests[0].allocate(task, requests[1])
                else:
                    for identifier, value in requests:
                        found = False
                        for resource in self.resources[resource_type]:
                            if resource.identifier == identifier:
                                resource.allocate(task, value)
                                found = True
                                break
                        if not found:
                            task.log.write('Resource "%s" with identifier="%s" not found' % (
                                resource_type, identifier))
                            raise RuntimeError('Resource "%s" with identifier="%s" not found' % (
                                resource_type, identifier))

            task.current_resources = resources
            return True

        except Exception as e:
            self.task_error(task, e)
            self.release_resources(task, resources)
        pass

    def release_resources(self, task, resources):
        self.status_update = True
        for resource_type, requests in resources.iteritems():
            if resource_type == "gpus":
                requests[0].deallocate(task)
            else:
                for identifier, value in requests:
                    for resource in self.resources[resource_type]:
                        if resource.identifier == identifier:
                            resource.deallocate(task)
                            self.emit_gpus_available()
        task.current_resources = None

    def run_task(self, task, resources):
        """
        Executes a task

        Arguments:
        task -- the task to run
        resources -- the resources allocated for this task
            a dict mapping resource_type to lists of (identifier, value) tuples
        """
        try:
            task.run(resources, sch_obj=self)
        except Exception as e:
            self.task_error(task, e)
        finally:
            if task.flag != "deployment_task":
                self.release_resources(task, resources)


    def emit_gpus_available(self):
        """
        Call socketio.emit gpu availability
        """
        from hyperai.webapp import scheduler, socketio
        socketio.emit('server update',
                      {
                          'update': 'gpus_available',
                          'total_gpu_count': self.resources['gpus'].get_gpu_max(),  # +++
                          'remaining_gpu_count': self.resources['gpus'].remaining(),  # +++
                      },
                      namespace='/jobs',
                      room='job_management'
                      )

    @staticmethod
    def set_user_gpu():
        path = '/root/hyperai/deploy_gpu.txt'
        # path = os.path.join(config_value('public_dir'), 'gpu1.txt')
        if os.path.exists(path):
            with open(path, 'r+') as f:
                a = f.read()
                b = json.loads(a)
                print 'set_redis'
                for i, p in b.items():
                    r.set('{}_gpu'.format(i), p)
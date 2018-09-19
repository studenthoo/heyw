# Copyright (c) 2014-2017, NVIDIA CORPORATION.  All rights reserved.
from __future__ import absolute_import

from . import tasks
from hyperai.job import Job
from hyperai.utils import override
from hyperai.status import Status
# from hyperai.ext import r

# NOTE: Increment this every time the pickled object changes
PICKLE_VERSION = 1


class ModelJob(Job):
    """
    A Job that creates a neural network model
    """

    def __init__(self, dataset_id, **kwargs):
        """
        Arguments:
        dataset_id -- the job_id of the DatasetJob that this ModelJob depends on
        """
        super(ModelJob, self).__init__(**kwargs)
        self.pickver_job_dataset = PICKLE_VERSION

        self.dataset_id = dataset_id
        self.load_dataset()

    def __getstate__(self):
        state = super(ModelJob, self).__getstate__()
        if 'dataset' in state:
            del state['dataset']
        return state

    def __setstate__(self, state):
        super(ModelJob, self).__setstate__(state)
        self.dataset = None

    @override
    def json_dict(self, verbose=False):
        d = super(ModelJob, self).json_dict(verbose)
        d['dataset_id'] = self.dataset_id

        if verbose:
            d.update({
                'snapshots': [s[1] for s in self.train_task().snapshots],
            })
        return d

    def load_dataset(self):
        from hyperai.webapp import scheduler
        job = scheduler.get_job(self.dataset_id)
        assert job is not None, 'Cannot find dataset'
        self.dataset = job
        for task in self.tasks:
            task.dataset = job

    def train_task(self):
        """Return the first TrainTask for this job"""
        return [t for t in self.tasks if isinstance(t, tasks.TrainTask)][0]

    def download_files(self):
        """
        Returns a list of tuples: [(path, filename)...]
        These files get added to an archive when this job is downloaded
        """
        return NotImplementedError()

    # def release_res_about_user(self):
    #     username = self.username
    #     # print "\n* [{id}] - [{username}] - {status}".format(id=self.id(), username=username, status=self.status)
    #     gpu_num = 0
    #     for task in self.tasks:
    #         gpu_ = int(task.gpu_count) * int(task.node_count)
    #         gpu_num += gpu_
    #     gpu_used_old = r.get("{}_gpu".format(username))
    #     if gpu_used_old is not None:
    #         gpu_used_new = (int(gpu_used_old) - gpu_num) if (int(gpu_used_old) - gpu_num) >= 0 else 0
    #         r.set("{}_gpu".format(username), gpu_used_new)
    #     else:
    #         r.set("{}_gpu".format(username), 0)
    #     self.tasks[0].logger.info("Release GPU: {username} - {num}\n".format(username=username, num=gpu_num))
        # print "* [{job_id}] - [{job_status}] - [{username}] release gpu: {num}\n".format(job_id=self.id(),
        #                                                                                  job_status=self.status,
        #                                                                                  username=username,
        #                                                                                  num=gpu_num)




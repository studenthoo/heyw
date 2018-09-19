# Copyright (c) 2014-2017, NVIDIA CORPORATION.  All rights reserved.
# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging
import os.path
import platform
import re
import signal
import subprocess
import time

import flask
import gevent.event

from . import utils
from .config import config_value
from .status import Status, StatusCls
import hyperai.log

# NOTE: Increment this every time the pickled version changes
PICKLE_VERSION = 1


class Task(StatusCls):
    """
    Base class for Tasks
    A Task is a compute-heavy operation that runs in a separate executable
    Communication is done by processing the stdout of the executable
    """

    def __init__(self, job_dir, parents=None):
        super(Task, self).__init__()
        self.pickver_task = PICKLE_VERSION

        self.job_dir = job_dir
        self.job_id = os.path.basename(job_dir)

        self.task_id = '%s' % (os.urandom(2).encode('hex'))
        if parents is None:
            self.parents = None
        elif isinstance(parents, (list, tuple)):
            self.parents = parents
        elif isinstance(parents, Task):
            self.parents = [parents]
        else:
            raise TypeError('parents is %s' % type(parents))

        self.exception = None
        self.traceback = None
        self.aborted = gevent.event.Event()
        self.set_logger()
        self.p = None  # Subprocess object for training
        self.flag = None
        self._pri = 1

    def __getstate__(self):
        d = self.__dict__.copy()

        if 'aborted' in d:
            del d['aborted']
        if 'logger' in d:
            del d['logger']
        if 'sch_obj' in d:
            del d['sch_obj']
        if 'p' in d:
            # Subprocess object for training is not pickleable
            del d['p']
        return d

    def __setstate__(self, state):
        self.__dict__ = state

        self.aborted = gevent.event.Event()
        self.set_logger()

    def set_logger(self):
        self.logger = hyperai.log.JobIdLoggerAdapter(
            logging.getLogger('hyperai.webapp'),
            {'job_id': self.job_id},
        )

    def get_pri(self):
        return self._pri

    def ch_pri(self):
        """Only administrators have authority"""
        pass

    def name(self):
        """
        Returns a string
        """
        raise NotImplementedError

    def html_id(self):
        """
        Returns a string
        """
        return 'task-%s' % id(self)

    def on_status_update(self):
        """
        Called when StatusCls.status.setter is used
        """
        from hyperai.webapp import app, socketio

        # Send socketio updates
        message = {
            'task': self.html_id(),
            'update': 'status',
            'status': self.status.name,
            'css': self.status.css,
            'show': (self.status in [Status.RUN, Status.ERROR]),
            'running': self.status.is_running(),
        }
        with app.app_context():
            message['html'] = flask.render_template('status_updates.html',
                                                    updates=self.status_history,
                                                    exception=self.exception,
                                                    traceback=self.traceback,
                                                    )

        socketio.emit('task update',
                      message,
                      namespace='/jobs',
                      room=self.job_id,
                      )

        from hyperai.webapp import scheduler
        job = scheduler.get_job(self.job_id)
        if job:
            job.on_status_update()

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

    def ready_to_queue(self):
        """
        Returns True if all parents are done
        """
        if not self.parents:
            return True
        for parent in self.parents:
            if parent.status != Status.DONE:
                return False
        return True

    def offer_resources(self, resources):
        """
        Check the available resources and return a set of requested resources

        Arguments:
        resources -- a copy of scheduler.resources
        """
        raise NotImplementedError

    def task_arguments(self, resources, env):
        """
        Returns args used by subprocess.Popen to execute the task
        Returns False if the args cannot be set properly

        Arguments:
        resources -- the resources assigned by the scheduler for this task
        environ   -- os.environ instance to run process in
        """
        raise NotImplementedError

    def before_run(self):
        """
        Called before run() executes
        Raises exceptions
        """
        pass

    def run(self, resources, **kwargs):
        """
        Execute the task

        Arguments:
        resources -- the resources assigned by the scheduler for this task
        """
        self.sch_obj = kwargs['sch_obj']

        self.before_run()

        env = os.environ.copy()
        args, resources_args = self.task_arguments(resources, env)

        if not args:
            self.logger.error('Could not create the arguments for Popen')
            self.status = Status.ERROR
            return False
        # Convert them all to strings
        args = [str(x) for x in args]

        self.logger.info('%s task started.' % self.name())
        self.status = Status.RUN

        unrecognized_output = []

        import sys
        env['PYTHONPATH'] = os.pathsep.join(['.', self.job_dir, env.get('PYTHONPATH', '')] + sys.path)
        if platform.system() == 'Windows':
            args = ' '.join(args)
            self.logger.info('Task subprocess args: "{}"'.format(args))
        else:
            self.logger.info('Task subprocess args: "%s"' % ' '.join(args))

        if self.flag:
            flag = self.flag
        else:
            flag = "other"
        """
        ds-parse-s3
        ds-create-generic-db
        ds-create-db
        ds-analyze-db
        ds-parse-folder
        inference
        caffe-train
        tf-train
        torch-train
        """

        ds_task_list = ['ds-parse-folder', 'ds-create-db', 'inference', 'ds-create-generic-db','extra-ds-task']
        if flag not in ds_task_list:
            exe = "/usr/bin/python2"
            new_path = os.path.join(os.path.dirname(os.path.abspath(hyperai.__file__)), 'tools', 'kuber',
                                    'main_kube.py')
            # if flag == "torch-train":
            if flag == "caffe-train" or flag == "torch-train":
                flag_args = []
                pycaffe_file = '/root/hyperai/hyperai/pid_rand.py'
                args = ' '.join(args)
                flag_args.append(pycaffe_file)
                flag_args.append('--args=%s' % args)
                new_args = [exe, str(new_path),
                            "--flag=%s" % flag,
                            "--job_id=%s" % (self.job_id,),
                            "--task_id=%s" % (self.task_id,),
                            "--command=%s" % exe,
                            "--argument=%s" % flag_args]
            else:
                new_args = [exe, str(new_path),
                            "--flag=%s" % flag,
                            "--job_id=%s" % (self.job_id,),
                            "--task_id=%s" % (self.task_id,),
                            "--command=%s" % (args[0],),
                            "--argument=%s" % (args[1:],)]

            main_process_start = time.time()
            new_args.append("--main_process_start=%s" % main_process_start)

            if 'gpu_count' in resources_args and resources_args['gpu_count']:
                new_args.append("--gpu_count=%s" % resources_args['gpu_count'])
            else:
                new_args.append("--gpu_count=%s" % 0)
            if 'cpu_count' in resources_args and resources_args['cpu_count']:
                new_args.append("--cpu_count=%s" % resources_args['cpu_count'])
            else:
                new_args.append("--cpu_count=%s" % 4)
            if 'memory_count' in resources_args and resources_args['memory_count']:
                new_args.append("--memory_count=%s" % resources_args['memory_count'])
            else:
                new_args.append("--memory_count=%s" % "16Gi")

            new_args.append("--nfsdir=%s" % config_value('jobs_dir'))

            print "The kubernetes task [%s] start..." % flag
            self.p = subprocess.Popen(args=new_args,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT,
                                      cwd=self.job_dir,
                                      close_fds=False if platform.system() == 'Windows' else True,
                                      env=env, )
        else:
            print "Not by kubernets."
            self.p = subprocess.Popen(args,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT,
                                      cwd=self.job_dir,
                                      close_fds=False if platform.system() == 'Windows' else True,
                                      env=env,
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
                        # Remove whitespace
                        line = line.strip()
                    sys.stdout.flush()
                    if line:
                        # print line
                        if not self.process_output(line):
                            self.logger.warning('%s unrecognized output: %s' % (self.name(), line.strip()))
                            unrecognized_output.append(line)
                    else:
                        time.sleep(0.05)
                if sigterm_time is not None and (time.time() - sigterm_time > sigterm_timeout):
                    self.p.send_signal(signal.SIGKILL)
                    self.logger.warning('Sent SIGKILL to task "%s"' % self.name())
                    time.sleep(0.05)
                time.sleep(0.01)
        except:
            self.p.terminate()
            self.after_run()
            raise

        self.after_run()

        if self.status != Status.RUN:
            return False
        elif self.p.returncode != 0:
            self.logger.error('%s task failed with error code %d' % (self.name(), self.p.returncode))
            if self.exception is None:
                self.exception = 'error code %d' % self.p.returncode
                if unrecognized_output:
                    if self.traceback is None:
                        self.traceback = '\n'.join(unrecognized_output)
                    else:
                        self.traceback = self.traceback + ('\n'.join(unrecognized_output))
            self.after_runtime_error()
            self.status = Status.ERROR
            return False
        else:
            self.logger.info('%s task completed.' % self.name())
            self.status = Status.DONE
            return True

    def abort(self):
        """
        Abort the Task
        """
        if self.status.is_running():
            self.aborted.set()
            self.status = Status.ABORT
            # if hasattr(self, 'job'):
            #     self.del_pod(job_id=self.job.id())

    def preprocess_output_hyperai(self, line):
        """
        Takes line of output and parses it according to hyperai's log format
        Returns (timestamp, level, message) or (None, None, None)
        """
        # NOTE: This must change when the logging format changes
        # YYYY-MM-DD HH:MM:SS [LEVEL] message
        match = re.match(r'(\S{10} \S{8}) \[(\w+)\s*\] (.*)$', line)
        if match:
            timestr = match.group(1)
            timestamp = time.mktime(time.strptime(timestr, hyperai.log.DATE_FORMAT))
            level = match.group(2)
            message = match.group(3)
            if level.startswith('DEB'):
                level = 'debug'
            elif level.startswith('INF'):
                level = 'info'
            elif level.startswith('WAR'):
                level = 'warning'
            elif level.startswith('ERR'):
                level = 'error'
            elif level.startswith('CRI'):
                level = 'critical'
            return (timestamp, level, message)
        else:
            return (None, None, None)

    def process_output(self, line):
        """
        Process a line of output from the task
        Returns True if the output was able to be processed

        Arguments:
        line -- a line of output
        """
        raise NotImplementedError

    def est_done(self):
        """
        Returns the estimated time in seconds until the task is done
        """
        if self.status != Status.RUN or self.progress == 0:
            return None
        elapsed = time.time() - self.status_history[-1][1]
        return (1 - self.progress) * elapsed // self.progress

    def after_run(self):
        """
        Called after run() executes
        """
        pass

    def after_runtime_error(self):
        """
        Called after a runtime error during run()
        """
        pass

    def emit_progress_update_old(self):
        """
        Call socketio.emit for task progress update, and trigger job progress update.
        """
        from hyperai.webapp import socketio
        socketio.emit('task update',
                      {
                          'task': self.html_id(),
                          'update': 'progress',
                          'percentage': int(round(100 * self.progress)),
                          'eta': utils.time_filters.print_time_diff(self.est_done()),
                      },
                      namespace='/jobs',
                      room=self.job_id,
                      )

        from hyperai.webapp import scheduler
        job = scheduler.get_job(self.job_id)
        if job:
            job.emit_progress_update()

    def emit_progress_update(self):
        """
        Call socketio.emit for task progress update, and trigger job progress update.
        """
        from hyperai.webapp import socketio
        socketio.emit('task update',
                      {
                          'task': self.html_id(),
                          'update': 'progress',
                          'percentage': int(round(100 * self.progress)),
                          'eta': utils.time_filters.print_time_diff(self.est_done()),
                          'features': self.dbs['features'] if self.dbs else None,
                      },
                      namespace='/jobs',
                      room=self.job_id,
                      )

        from hyperai.webapp import scheduler
        job = scheduler.get_job(self.job_id)

        if job:
            job.emit_progress_update()

    def del_pod(self, job_id=None):
        pass

# Copyright (c) 2014-2017, NVIDIA CORPORATION.  All rights reserved.
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from collections import OrderedDict, namedtuple
import os.path
import time
import subprocess
import re
import platform

import flask
import gevent
import psutil
import signal

from hyperai import device_query
from hyperai.task import Task
from hyperai.status import Status
from hyperai import utils
from hyperai.utils import subclass, override
from hyperai.utils.manage_kuber import ManagePod
from hyperai.utils import read_process_stdout
from hyperai.utils.resource_monitor import Monitor
from hyperai.users import register_user

# NOTE: Increment this every time the picked object changes
PICKLE_VERSION = 2

# Used to store network outputs
NetworkOutput = namedtuple('NetworkOutput', ['kind', 'data'])


@subclass
class TrainTask(Task):
    """
    Defines required methods for child classes
    """

    def __init__(self, job, dataset, train_epochs, snapshot_interval, learning_rate, lr_policy, **kwargs):
        """
        Arguments:
        job -- model job
        dataset -- a DatasetJob containing the dataset for this model
        train_epochs -- how many epochs of training data to train on
        snapshot_interval -- how many epochs between taking a snapshot
        learning_rate -- the base learning rate
        lr_policy -- a hash of options to be used for the learning rate policy

        Keyword arguments:
        gpu_count -- how many GPUs to use for training (integer)
        selected_gpus -- a list of GPU indexes to be used for training
        batch_size -- if set, override any network specific batch_size with this value
        batch_accumulation -- accumulate gradients over multiple batches
        val_interval -- how many epochs between validating the model with an epoch of validation data
        traces_interval -- amount of steps in between timeline traces
        pretrained_model -- filename for a model to use for fine-tuning
        crop_size -- crop each image down to a square of this size
        use_mean -- subtract the dataset's mean file or mean pixel
        random_seed -- optional random seed
        data_aug -- data augmentation options
        """
        self.gpu_count = kwargs.pop('gpu_count', None)
        self.cpu_count = kwargs.pop('cpu_count', None)
        self.memory_count = kwargs.pop('memory_count', None)
        self.node_count = kwargs.pop('node_count', 1)
        self.node_label = kwargs.pop('node_label', None)
        # print '* self.node_label=',self.node_label

        self.selected_gpus = kwargs.pop('selected_gpus', None)
        self.batch_size = kwargs.pop('batch_size', None)
        self.batch_accumulation = kwargs.pop('batch_accumulation', None)
        self.val_interval = kwargs.pop('val_interval', None)
        self.traces_interval = kwargs.pop('traces_interval', None)
        self.pretrained_model = kwargs.pop('pretrained_model', None)
        self.crop_size = kwargs.pop('crop_size', None)
        self.use_mean = kwargs.pop('use_mean', None)
        self.random_seed = kwargs.pop('random_seed', None)
        self.solver_type = kwargs.pop('solver_type', None)
        self.rms_decay = kwargs.pop('rms_decay', None)
        self.shuffle = kwargs.pop('shuffle', None)
        self.network = kwargs.pop('network', None)
        self.framework_id = kwargs.pop('framework_id', None)
        self.data_aug = kwargs.pop('data_aug', None)
        self.dbs = None
        self.desc = kwargs.pop('desc',None)
        self.mpi = kwargs.pop('mpi',None)
        super(TrainTask, self).__init__(job_dir=job.dir(), **kwargs)
        self.pickver_task_train = PICKLE_VERSION

        self.job = job
        self.dataset = dataset
        self.train_epochs = train_epochs
        self.snapshot_interval = snapshot_interval
        self.learning_rate = learning_rate
        self.lr_policy = lr_policy

        self.current_epoch = 0
        self.snapshots = []
        self.timeline_traces = []

        # data gets stored as dicts of lists (for graphing)
        self.train_outputs = OrderedDict()
        self.val_outputs = OrderedDict()

        register_user.allocate_resources(self.job.username, self)

    def __getstate__(self):
        state = super(TrainTask, self).__getstate__()
        if 'dataset' in state:
            del state['dataset']
        if 'snapshots' in state:
            del state['snapshots']
        if '_labels' in state:
            del state['_labels']
        if '_hw_socketio_thread' in state:
            del state['_hw_socketio_thread']
        if 'sch_obj' in state:
            del state['sch_obj']
        if 'pod_obj' in state:
            del state['pod_obj']
        if 'yaml_path' in state:
            del state['yaml_path']
        return state

    def __setstate__(self, state):
        if state['pickver_task_train'] < 2:
            state['train_outputs'] = OrderedDict()
            state['val_outputs'] = OrderedDict()

            tl = state.pop('train_loss_updates', None)
            vl = state.pop('val_loss_updates', None)
            va = state.pop('val_accuracy_updates', None)
            lr = state.pop('lr_updates', None)
            if tl:
                state['train_outputs']['epoch'] = NetworkOutput('Epoch', [x[0] for x in tl])
                state['train_outputs']['loss'] = NetworkOutput('SoftmaxWithLoss', [x[1] for x in tl])
                state['train_outputs']['learning_rate'] = NetworkOutput('LearningRate', [x[1] for x in lr])
            if vl:
                state['val_outputs']['epoch'] = NetworkOutput('Epoch', [x[0] for x in vl])
                if va:
                    state['val_outputs']['accuracy'] = NetworkOutput('Accuracy', [x[1] / 100 for x in va])
                state['val_outputs']['loss'] = NetworkOutput('SoftmaxWithLoss', [x[1] for x in vl])

        if state['use_mean'] is True:
            state['use_mean'] = 'pixel'
        elif state['use_mean'] is False:
            state['use_mean'] = 'none'

        state['pickver_task_train'] = PICKLE_VERSION
        super(TrainTask, self).__setstate__(state)

        self.snapshots = []
        self.timeline_traces = []
        self.dataset = None

    @override
    def offer_resources(self, resources, locking_gpu=False):
        if locking_gpu:
            return None
        if 'gpus' not in resources:
            return None
        if not resources['gpus']:
            return {}  # don't use a GPU at all
        if self.gpu_count is not None:
            gpu_total = int(self.node_count) * int(self.gpu_count)
            if resources['gpus'].remaining(value=gpu_total):
                return {'gpus': (resources['gpus'], gpu_total)}
        return None

    def pre_allocate_res_task(self):
        # requested_resources = {'gpus': (resources['gpus'], gpu_total)}
        if hasattr(self, 'sch_obj') and self.sch_obj:
            requested_resources = {'gpus': (self.sch_obj.resources['gpus'], self.gpu_count)}
            try:
                self.sch_obj.reserve_resources(self, requested_resources)
                self.log.write("Success to allocate resource. \n")
                return True
            except Exception as e:
                self.sch_obj.task_error(self, e)
                # self.after_run()
                self.log.write("Failed to allocate resource. \n")
                raise ValueError("Failed to allocate resource.")
        else:
            self.log.write("Not Found Attribute. \n")
            return False

    @override
    def before_run(self, args=None):
        # start a thread which sends SocketIO updates about hardware utilization

        monitor = Monitor(self.job)
        self._hw_socketio_thread = gevent.spawn(monitor.hw_socketio_updater, self.job_id)
        # self._hw_socketio_thread = gevent.spawn(
        #     self.hw_socketio_updater, self.job_id)
        # pass

    def run(self, resources, **kwargs):
        """
        Execute the task

        Arguments:
        resources -- the resources assigned by the scheduler for this task
        """
        self.sch_obj = kwargs['sch_obj']

        env = os.environ.copy()
        args, res_args = self.task_arguments(resources, env)
        if not args:
            self.log.write('Could not create the arguments for Popen \n')
            self.logger.error('Could not create the arguments for Popen')
            self.status = Status.ERROR
            return False

        # Convert them all to strings
        args = [str(x) for x in args]

        obj_dict = self.before_run(args=args)

        self.log.write('----*----%s task started.----*---- \n' % self.name())
        self.logger.info('%s task started.' % self.name())


        unrecognized_output = []

        import sys
        env['PYTHONPATH'] = os.pathsep.join(['.', self.job_dir, env.get('PYTHONPATH', '')] + sys.path)

        # https://docs.python.org/2/library/subprocess.html#converting-argument-sequence
        if platform.system() == 'Windows':
            args = ' '.join(args)
            self.log.write('Task subprocess args: "{}"\n'.format(args))
            self.logger.info('Task subprocess args: "{}"'.format(args))
        else:
            self.log.write('Task subprocess args: "%s"' % ' \n'.join(args))
            self.logger.info('Task subprocess args: "%s"' % ' '.join(args))

        try:
            # if not obj_dict['obj'].create_pod(obj_dict['obj'].yaml_path):
            #     return False
            val = obj_dict['obj'].create_pod(obj_dict['obj'].yaml_path)
            if not val:
                self.log.write("\nPod has been DEL while the status was Pending\n")
                self.after_run()
                return False
        except Exception as e:
            self.log.write("Create Pod Failed: %s \n" % e)
            self.after_run()
            raise RuntimeError("Create Pod Failed: %s " % e)
        self.logger.info("Created Pod Successed. ")
        self.log.write("----*----Created Pod Successed.----*---- \n")
        self.status = Status.RUN

        pod_name = obj_dict['obj'].pod_name
        log_com = "kubectl logs -f {}".format(pod_name)
        self.logger.info('Task Start ...')
        self.log.write("----*----Task Start ...----*---- \n")
        self.p = subprocess.Popen(log_com, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  cwd=self.job_dir, env=env,
                                  close_fds=False if platform.system() == 'Windows' else True,
                                  shell=True)
        try:
            sigterm_time = None  # When was the SIGTERM signal sent
            sigterm_timeout = 2  # When should the SIGKILL signal be sent
            while self.p.poll() is None:
                for line in utils.nonblocking_readlines(self.p.stdout):
                    if self.aborted.is_set():
                        if sigterm_time is None:
                            # Attempt graceful shutdown
                            sigterm_time = time.time()
                            self.status = Status.ABORT
                            self.p.send_signal(signal.SIGTERM)
                        break

                    if line is not None:
                        # Remove whitespace
                        line = line.strip()

                    if line:
                        # print '====>>>', line
                        value = self.process_output(line)
                        if not value:
                            self.logger.warning('%s unrecognized output: %s' % (self.name(), line.strip()))
                            unrecognized_output.append(line)
                        elif value == "E":
                            self.after_runtime_error()
                            # print "* * train.py/run: Set Task Status To Error ."
                            self.status = Status.ERROR
                            # print "* * train.py/run: Kill The Subprocess ."
                            self.p.terminate()
                            # self.after_run()
                            break
                            # return False
                    else:
                        time.sleep(0.6)
                if sigterm_time is not None and (time.time() - sigterm_time > sigterm_timeout):
                    self.p.send_signal(signal.SIGKILL)
                    self.logger.warning('Sent SIGKILL to task "%s"' % self.name())
                    self.log.write('Sent SIGKILL to task "%s"' % self.name())
                    time.sleep(0.1)
                time.sleep(0.01)
        except Exception as e:
            self.p.terminate()
            self.log.write("%s" % e)
            self.after_run()
            raise
        self.after_run()

        if self.status != Status.RUN:
            return False
        elif self.p.returncode != 0:
            self.logger.error('%s task failed with error code %d' % (self.name(), self.p.returncode))
            # self.log.write('%s task failed with error code %d' % (self.name(), self.p.returncode))
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
            # self.log.write('%s task completed.' % self.name())
            # self.log.close()
            self.status = Status.DONE
            return True

    def exec_command(self, command, symbool=None):
        if symbool:
            command = "sudo {}".format(command)
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        return read_process_stdout(p)
        # res = p.stdout.read()
        # return res

    def get_full_pod_name(self, res, pod_base_name):
        """
        :param pod_base_name:
        :param res: last get pods result
        :return: full_pod_name  str
        """
        pattern = re.compile(r'\S*{}\S*'.format(pod_base_name))
        if res:
            pod_name_list = re.findall(pattern, res)
            if pod_name_list:
                return pod_name_list
            else:
                return None
        pass

    def parse_gpu_msg(self, lines=None):
        # get the message of gpu about pod (memory, utilization, temperature, ...)
        line = lines.strip().split('Device')

        name_pattern = re.compile(r'name')
        major_pattern = re.compile(r'major')
        minor_pattern = re.compile(r'minor')
        memory_utilization_pattern = re.compile(r'Memory utilization')
        gpu_utilization_pattern = re.compile(r'GPU utilization ')
        total_memory_pattern = re.compile(r'Total memory')
        used_memory_pattern = re.compile(r'Used memory')
        temperature_pattern = re.compile(r'Temperature')

        gpu_all_data = {}
        gpu_all_list = []
        for s in line:
            if s:
                if re.search(r'#\d+', s):
                    device_num = re.search(r'#\d+', s).group()
                else:
                    device_num = "##"
                line_list = s.split('\n')
                utilization_data = {}
                memory_data = {}
                temperature = ''
                name = ''
                major = ''
                minor = ''
                for line in line_list:
                    new_line = line.strip()
                    if re.search(memory_utilization_pattern, new_line):
                        memory_util = re.search('[0-9]+%', new_line).group()
                        if memory_util:
                            utilization_data['memory'] = memory_util
                    elif re.search(gpu_utilization_pattern, new_line):
                        gpu_util = re.search('[0-9]+%', new_line).group()
                        if gpu_util:
                            utilization_data['gpu'] = gpu_util
                    elif re.search(total_memory_pattern, new_line):
                        total_memory = re.search('[0-9]+', new_line).group()
                        if total_memory:
                            memory_data['total'] = "%s" % total_memory
                    elif re.search(used_memory_pattern, new_line):
                        used_memory = re.search('[0-9]+', new_line).group()
                        if used_memory:
                            memory_data['used'] = "%s" % used_memory
                    elif re.search(temperature_pattern, new_line):
                        temperature = re.search('[0-9]+', new_line).group()
                    elif re.search(name_pattern, new_line):
                        n = re.search('name\s*(\S?.*)', new_line).group(1)
                        name = n.strip()
                    elif re.search(major_pattern, new_line):
                        major = re.search('[0-9]+', new_line).group()
                    elif re.search(minor_pattern, new_line):
                        minor = re.search('[0-9]+', new_line).group()

                if 'total' in memory_data and memory_data['total'] and 'used' in memory_data and memory_data['used']:
                    # free_memory = int(memory_data['total']) - int(memory_data['used'])
                    free_memory = int(memory_data['total']) - int(memory_data['used'])
                    memory_data['free'] = "%s" % str(free_memory)
                gpu_all_data[device_num] = {'utilization': utilization_data, 'memory': memory_data,
                                            'temperature': temperature, 'name': name, 'major': major, 'minor': minor}
                gpu_all_list.append({'utilization': utilization_data, 'memory': memory_data,
                                     'temperature': temperature, 'name': name, 'major': major, 'minor': minor})
        return gpu_all_data

    def get_gpu_from_pod(self, pod_name_list):
        gpu_msg_list = []
        for pod in pod_name_list:
            device_query_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                             'device_query.py')
            get_gpu_from_pod = "kubectl exec {} python {}".format(pod, device_query_file)
            res2 = self.exec_command(get_gpu_from_pod)
            if res2:
                res = self.parse_gpu_msg(res2)
                res['container_name'] = pod
                gpu_msg_list.append(res)
            else:
                pass

        return gpu_msg_list  # [[{1}, {2}, ...], [{1}, {2}, ...], ...]

    def get_gpu_msg(self, pod_base_name):

        get_pods_command = "kubectl get po -o wide"
        for i in range(10):
            res1 = self.exec_command(get_pods_command)
            if res1:
                full_pod_name_list = self.get_full_pod_name(res1, pod_base_name)
                if full_pod_name_list is not None and len(full_pod_name_list) > 0:
                    time.sleep(2)
                    get_gpu_from_pod_list = self.get_gpu_from_pod(full_pod_name_list)
                    return get_gpu_from_pod_list

            else:
                pass

    def hw_socketio_updater(self, pod_name):
        """
        This thread sends SocketIO messages about hardware utilization
        to connected clients

        Arguments:
        gpus -- a list of identifiers for the GPUs currently being used
        """
        from hyperai.webapp import app, socketio

        # this thread continues until killed in after_run()
        while True:
            # CPU (Non-GPU) Info
            data_cpu = {}
            # cpu_res = self.get_cpu_msg(pod_name)
            cpu_res = False
            if cpu_res:
                if cpu_res['memory']:
                    if cpu_res['memory']['free'] and cpu_res['memory']['cache'] and cpu_res['memory']['buff']:
                        data_cpu['mem_free'] = cpu_res['memory']['free']
                        data_cpu['mem_cache'] = cpu_res['memory']['cache']
                        data_cpu['mem_buff'] = cpu_res['memory']['buff']
                        data_cpu['mem_used'] = cpu_res['memory']['cache'] + cpu_res['memory']['buff']
                        data_cpu['men_total'] = data_cpu['mem_used'] + cpu_res['memory']['free']
                        data_cpu['mem_pct'] = data_cpu['mem_used']/data_cpu['men_total']
                if cpu_res['cpu']:
                    data_cpu['cpu_pct'] = cpu_res['cpu']['us']
            else:
                data_cpu = {'cpu_pct': 0, 'pid': 0, 'mem_pct': 0, 'mem_used': 0}

            data_gpu = []
            res = self.get_gpu_msg(pod_name)
            """
            res = [{'#0': {'major': '3', 
                           'temperature': '29', 
                           'utilization': {'gpu': '0%', 'memory': '0%'}, 
                           'memory': {'total': '4742', 'free': '4611', 'used': '131'}, 
                           'minor': '5', 'name': 'Tesla K20c'
                           }, 
                    'container_name': 'ljf-20180413-005612-e41f-6fcd56ff6-bq6bz'
                  }]
            """
            if res:
                for each in res:
                    """
                    each = {'#0': {'major': '3', 
                                   'temperature': '29', 
                                   'utilization': {'gpu': '0%', 'memory': '0%'}, 
                                   'memory': {'total': '4742', 'free': '4611', 'used': '131'}, 
                                   'minor': '5', 'name': 'Tesla K20c'
                                   }, 
                            'container_name': 'ljf-20180413-005612-e41f-6fcd56ff6-bq6bz'
                            }
                    """
                    if 'container_name' not in each:
                        each['container_name'] = "None"
                    container_list = []
                    update = {}
                    for key, val in each.items():
                        """
                        key ---- value =
                        #0 ---- {'major': '3', 
                                 'temperature': '29', 
                                 'utilization': {'gpu': '0%', 'memory': '0%'}, 
                                 'memory': {'total': '4742', 'free': '4611', 'used': '131'}, 
                                 'minor': '5', 
                                 'name': 'Tesla K20c'
                                 }
                        """
                        if key != 'container_name':
                            if each[key]['name'] and each[key]['utilization'] and each[key]['memory'] and each[key]['temperature']:
                                update = {'name': each[key]['name'],
                                          'index': key,
                                          'temperature': each[key]['temperature'],
                                          'memory': each[key]['memory'],
                                          'utilization': each[key]['utilization']}

                                update.update(each[key])
                                container_list.append(update)

                    data_gpu.append({'container_name': each['container_name'], 'value': container_list})
            """
            data_gpu=
            [{'value': [{'index': '#0', 'major': '3', 'name': 'Tesla K20c', 
                        'utilization': {'gpu': '0%', 'memory': '0%'}, 
                        'memory': {'total': '4742', 'free': '4611', 'used': '131'}, 
                        'minor': '5', 
                        'temperature': '29'
                        }], 
              'container_name': 'ljf-20180413-005612-e41f-6fcd56ff6-bq6bz'
            }]
            """
            with app.app_context():
                data = {'data_gpu': data_gpu, 'data_cpu': data_cpu}
                socketio.emit('task update',
                              {
                                  'task': self.html_id(),
                                  'update': 'gpu_utilization',
                                  'data': data,
                              },
                              namespace='/jobs',
                              room=self.job_id,
                              )
            gevent.sleep(1)

    def send_progress_update(self, epoch):
        """
        Sends socketio message about the current progress
        """
        if self.current_epoch == epoch:
            return

        self.current_epoch = epoch
        self.progress = epoch / self.train_epochs
        self.emit_progress_update()

    def save_train_output(self, *args):
        """
        Save output to self.train_outputs
        """
        from hyperai.webapp import socketio

        if not self.save_output(self.train_outputs, *args):
            return

        if self.last_train_update and (time.time() - self.last_train_update) < 5:
            return
        self.last_train_update = time.time()

        self.logger.debug('Training %s%% complete.' % round(100 * self.current_epoch / self.train_epochs, 2))

        # loss graph data
        data = self.combined_graph_data()
        if data:
            socketio.emit('task update',
                          {
                              'task': self.html_id(),
                              'update': 'combined_graph',
                              'data': data,
                          },
                          namespace='/jobs',
                          room=self.job_id,
                          )

            if data['columns']:
                # isolate the Loss column data for the sparkline
                graph_data = data['columns'][0][1:]
                socketio.emit('task update',
                              {
                                  'task': self.html_id(),
                                  'job_id': self.job_id,
                                  'update': 'combined_graph',
                                  'data': graph_data,
                              },
                              namespace='/jobs',
                              room='job_management',
                              )

        # lr graph data
        data = self.lr_graph_data()
        if data:
            socketio.emit('task update',
                          {
                              'task': self.html_id(),
                              'update': 'lr_graph',
                              'data': data,
                          },
                          namespace='/jobs',
                          room=self.job_id,
                          )

    def save_val_output(self, *args):
        """
        Save output to self.val_outputs
        """
        from hyperai.webapp import socketio

        if not self.save_output(self.val_outputs, *args):
            return

        # loss graph data
        data = self.combined_graph_data()
        if data:
            socketio.emit('task update',
                          {
                              'task': self.html_id(),
                              'update': 'combined_graph',
                              'data': data,
                          },
                          namespace='/jobs',
                          room=self.job_id,
                          )

    def save_output(self, d, name, kind, value):
        """
        Save output to self.train_outputs or self.val_outputs
        Returns true if all outputs for this epoch have been added

        Arguments:
        d -- the dictionary where the output should be stored
        name -- name of the output (e.g. "accuracy")
        kind -- the type of outputs (e.g. "Accuracy")
        value -- value for this output (e.g. 0.95)
        """
        # don't let them be unicode
        name = str(name)
        kind = str(kind)

        # update d['epoch']
        if 'epoch' not in d:
            d['epoch'] = NetworkOutput('Epoch', [self.current_epoch])
        elif d['epoch'].data[-1] != self.current_epoch:
            d['epoch'].data.append(self.current_epoch)

        if name not in d:
            d[name] = NetworkOutput(kind, [])
        epoch_len = len(d['epoch'].data)
        name_len = len(d[name].data)

        # save to back of d[name]
        if name_len > epoch_len:
            raise Exception('Received a new output without being told the new epoch')
        elif name_len == epoch_len:
            # already exists
            if isinstance(d[name].data[-1], list):
                d[name].data[-1].append(value)
            else:
                d[name].data[-1] = [d[name].data[-1], value]
        elif name_len == epoch_len - 1:
            # expected case
            d[name].data.append(value)
        else:
            # we might have missed one
            for _ in xrange(epoch_len - name_len - 1):
                d[name].data.append(None)
            d[name].data.append(value)

        for key in d:
            if key not in ['epoch', 'learning_rate']:
                if len(d[key].data) != epoch_len:
                    return False
        return True

    @override
    def after_run(self):
        if hasattr(self, '_hw_socketio_thread'):
            self._hw_socketio_thread.kill()

    def detect_snapshots(self):
        """
        Populate self.snapshots with snapshots that exist on disk
        Returns True if at least one usable snapshot is found
        """
        return False

    def snapshot_list(self):
        """
        Returns an array of arrays for creating an HTML select field
        """
        return [[s[1], 'Epoch #%s' % s[1]] for s in reversed(self.snapshots)]

    def est_next_snapshot(self):
        """
        Returns the estimated time in seconds until the next snapshot is taken
        """
        return None

    def can_view_weights(self):
        """
        Returns True if this Task can visualize the weights of each layer for a given model
        """
        raise NotImplementedError()

    def view_weights(self, model_epoch=None, layers=None):
        """
        View the weights for a specific model and layer[s]
        """
        return None

    def can_view_activations(self):
        """
        Returns True if this Task can visualize the activations of a model after inference
        """
        raise NotImplementedError()

    def infer_one(self, data, model_epoch=None, layers=None):
        """
        Run inference on one input
        """
        return None

    def can_infer_many(self):
        """
        Returns True if this Task can run inference on many inputs
        """
        raise NotImplementedError()

    def infer_many(self, data, model_epoch=None):
        """
        Run inference on many inputs
        """
        return None

    def get_snapshot(self, epoch=-1, download=False):
        """
        return snapshot file for specified epoch
        """
        snapshot_filename = None

        if len(self.snapshots) == 0:
            return "no snapshots"

        if epoch == -1 or not epoch:
            epoch = self.snapshots[-1][1]
            snapshot_filename = self.snapshots[-1][0]
        else:
            for f, e in self.snapshots:
                if e == epoch:
                    snapshot_filename = f
                    break
        if not snapshot_filename:
            raise ValueError('Invalid epoch')

        return snapshot_filename

    def get_snapshot_filename(self, epoch=-1):
        """
        Return the filename for the specified epoch
        """
        path, name = os.path.split(self.get_snapshot(epoch))
        return name

    def get_labels(self):
        """
        Read labels from labels_file and return them in a list
        """
        # The labels might be set already
        if hasattr(self, '_labels') and self._labels and len(self._labels) > 0:
            return self._labels

        assert hasattr(self.dataset, 'labels_file'), 'labels_file not set'
        assert self.dataset.labels_file, 'labels_file not set'
        assert os.path.exists(self.dataset.path(self.dataset.labels_file)), 'labels_file does not exist: {}'.format(
            self.dataset.path(self.dataset.labels_file)
        )

        labels = []
        with open(self.dataset.path(self.dataset.labels_file)) as infile:
            for line in infile:
                label = line.strip()
                if label:
                    labels.append(label)

        assert len(labels) > 0, 'no labels in labels_file'

        self._labels = labels
        return self._labels

    def lr_graph_data(self):
        """
        Returns learning rate data formatted for a C3.js graph

        Keyword arguments:

        """
        if not self.train_outputs or 'epoch' not in self.train_outputs or 'learning_rate' not in self.train_outputs:
            return None

        # return 100-200 values or fewer
        stride = max(len(self.train_outputs['epoch'].data) / 100, 1)
        e = ['epoch'] + self.train_outputs['epoch'].data[::stride]
        lr = ['lr'] + self.train_outputs['learning_rate'].data[::stride]
        for index,i in enumerate(lr):
            if i is None:
                lr[index] = lr[index-1]
        return {
            'columns': [e, lr],
            'xs': {
                'lr': 'epoch'
            },
            'names': {
                'lr': 'Learning Rate'
            },
        }

    def detect_timeline_traces(self):
        """
        Populate self.timeline_traces with snapshots that exist on disk
        Returns True if at least one usable snapshot is found
        """
        return False

    def has_timeline_traces(self):
        """
        Evaluates if there are timeline traces to be viewed at all
        """
        return len(self.timeline_traces) > 0

    def timeline_trace(self, tid):
        """
        Returns the data of a selected timeline trace
        """
        for item in self.timeline_traces:
            if item[1] == tid:
                fn = item[0]
                with open(fn, 'r') as file_data:
                    return file_data.read()

        raise ValueError('Requested timeline not found in timeline list')

    def timeline_trace_list(self):
        """
        Returns an array of timeline trace id's for creating an HTML select field
        """
        return [[s[1], 'Trace #%s' % s[1]] for s in reversed(self.timeline_traces)]

    def combined_graph_data(self, cull=True):
        """
        Returns all train/val outputs in data for one C3.js graph

        Keyword arguments:
        cull -- if True, cut down the number of data points returned to a reasonable size
        """
        data = {
            'columns': [],
            'xs': {},
            'axes': {},
            'names': {},
        }

        added_train_data = False
        added_val_data = False

        if self.train_outputs and 'epoch' in self.train_outputs:
            # print '------------------',self.train_outputs
            if cull:
                # max 200 data points
                stride = max(len(self.train_outputs['epoch'].data) / 100, 1)
            else:
                # return all data
                stride = 1
            for name, output in self.train_outputs.iteritems():
                if name not in ['epoch', 'learning_rate']:
                    col_id = '%s-train' % name
                    data['xs'][col_id] = 'train_epochs'
                    data['names'][col_id] = '%s (train)' % name
                    if 'accuracy' in output.kind.lower() or 'accuracy' in name.lower():
                        data['columns'].append([col_id] + [
                            (100 * x if x is not None else 'none')
                            for x in output.data[::stride]])
                        data['axes'][col_id] = 'y2'
                    else:
                        data['columns'].append([col_id] + [
                            (x if x is not None else 'none')
                            for x in output.data[::stride]])
                    added_train_data = True
        if added_train_data:
            data['columns'].append(['train_epochs'] + self.train_outputs['epoch'].data[::stride])

        if self.val_outputs and 'epoch' in self.val_outputs:
            if cull:
                # max 200 data points
                stride = max(len(self.val_outputs['epoch'].data) / 100, 1)
            else:
                # return all data
                stride = 1
            for name, output in self.val_outputs.iteritems():
                if name not in ['epoch']:
                    col_id = '%s-val' % name
                    data['xs'][col_id] = 'val_epochs'
                    data['names'][col_id] = '%s (val)' % name
                    if 'accuracy' in output.kind.lower() or 'accuracy' in name.lower():
                        data['columns'].append([col_id] + [
                            (100 * x if x is not None else 'none')
                            for x in output.data[::stride]])
                        data['axes'][col_id] = 'y2'
                    else:
                        data['columns'].append([col_id] + [
                            (x if x is not None else 'none')
                            for x in output.data[::stride]])
                    added_val_data = True
        if added_val_data:
            data['columns'].append(['val_epochs'] + self.val_outputs['epoch'].data[::stride])

        if added_train_data:
            # print '666666',data
            return data
        else:
            # return None if only validation data exists
            # helps with ordering of columns in graph
            return None

    # return id of framework used for training
    def get_framework_id(self):
        """
        Returns a string
        """
        return self.framework_id

    def get_model_files(self):
        """
        return path to model file
        """
        raise NotImplementedError()

    def get_network_desc(self):
        """
        return text description of model
        """
        raise NotImplementedError()

    def get_task_stats(self, epoch=-1):
        """
        return a dictionary of task statistics
        """
        raise NotImplementedError()

    # >>> add at 2018-6-14  >>>
    def del_pod_normal(self, job_id=None):
        try:
            get_res = self.short_exec_com()
            pod_name_list = self.parse_pod_name(job_id, get_res)
            if len(pod_name_list) > 0:
                pod_name = pod_name_list[0]
                del_cmd = "kubectl delete job {}".format(pod_name)
                msg = self.short_exec_com(command=del_cmd)
                # print "* * Delete pod by pod_name: %s " % msg
                return True
            else:
                print "Not Found Pod Name."
                return False
        except Exception as e:
            print "Delete Pod Failed: %s" % e

    def short_exec_com(self, command="kubectl get po -a -o wide"):
        p = subprocess.Popen(args=command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        return read_process_stdout(p)
        # return p.stdout.read()

    def parse_pod_name(self, element, content):
        return re.findall(r'\S*{}\S*'.format(element), content)
        # return re_findall_list

    def parse_pod_msg(self, element, content):
        one_pattern = re.compile(r'(\S*{}\S*)\s*(\S+)\s*(\S+)\s*'.format(element))
        all_find_list = re.search(one_pattern, content)
        if all_find_list:
            return [all_find_list.group(1), all_find_list.group(2), all_find_list.group(3)]
        else:
            return None
        pass

    def del_pod(self, job_id=None):
        try:
            # if self.status in (Status.RUN,):
            from hyperai.model.tasks.tensorflow_train_mpi import TensorflowTrainTaskMpi
            if hasattr(self, "pod_obj"):
                # print "* * model/task/train.py/del_pod:  [BF]  Del pod."
                self.pod_obj.delete_pod(job_id=self.job.id())
                # self.pod_obj.delete_pod()
            elif isinstance(self, TensorflowTrainTaskMpi):
                from hyperai.tools.mpi_kuber.mpi_kuber_coordinate import KubernetasCoord
                KubernetasCoord.delete_pods(job_id=self.job.id())
            else:
                # print "* * model/job.py/del_pod: [warn] Del pod normal ."
                self.del_pod_normal(job_id=self.job.id())
            return True
        except Exception as e:
            self.tasks[0].logger.info("Del Pod: [error] ", e)
    # <<< add at 2018-6-14  <<<

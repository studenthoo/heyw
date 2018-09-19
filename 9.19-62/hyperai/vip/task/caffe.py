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
from hyperai.config import config_value
import gevent
import gevent.event
import time
from hyperai.utils.resource_monitor import Monitor
from .train import TrainTask


class Caffe:
    def __init__(self, name, mode):
        self.name = name
        self.mode = mode

    def create_train_task(self, **kwargs):
        return CaffeTrain(name=self.name,mode=self.mode, **kwargs)


@subclass
class CaffeTrain(TrainTask):
    """
    分布式训练任务
    """

    CAFFE_LOG = 'au_caffe_output.log'

    def __init__(self, **kwargs):
        print "caffe kwargs :" ,kwargs
        super(CaffeTrain, self).__init__(**kwargs)
        self.base_path = kwargs['base_path']
        self.train_dir = kwargs['train_dir']
        self.test_dir = kwargs['test_dir']
        self.log_file = self.CAFFE_LOG
        self.caffe_log = None
        self.log = None
        self.temp_dict = {}
        self.temp_count = 0
        self.step = 0

    def __getstate__(self):
        state = super(CaffeTrain, self).__getstate__()
        if 'log' in state:
            del state['log']

        return state

    def __setstate__(self, state):
        super(CaffeTrain, self).__setstate__(state)


    @override
    def before_run(self):
        file_test_path = self.modification_test_file()
        file_path = self.modification_file(file_test_path)
        if self.mode == "single":
            self.log = open(self.path(self.CAFFE_LOG), 'a+')
            self.graph_data_txt = open(self.path(self.GRAPH_DATA_TXT), 'a+')

        self.args = ['caffe','train',
                     "--solver=%s" % (file_path),
                     "--gpu=all",
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
        print "args: %s" % (' '.join(self.args))
        try:
            kube_cood = KubernetasCoord(self.logger,
                                        self.log,
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
            monitor = Monitor(self.job)
            # print 'come in'
            self._hw_socketio_thread = gevent.spawn(monitor.hw_socketio_updater, self.job_id)
            return pod_name
        except Exception as e:
            self.job.state = 2
            self.log.write("Container Create Failed: %s" % e)
            raise IOError("Container Create Failed: %s" % e)

    def middle_run(self,line):
        if self.mode == "single":
            self.log.write('%s\n' % line)
            self.log.flush()

    @override
    def after_run(self):
        if self.mode == "single":
            print "* <VIP> delete pod......................"
            self.log.write("----*----delete pod ----*----")
            KubernetasCoord.delete_pods(job_id=self.job_id)
            self.log.close()
            self.graph_data_txt.close()

        super(CaffeTrain, self).after_run()

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
        ret = self.get_output_line_parameter(line)
        # print ret
        if ret:
            if ret.get("step"):
                self.step = ret.get("step")
                # self.temp_dict['step'] = ret.get("step")
            elif ret.get("value_loss"):
                if ret.get('name') == "Train":
                    self.temp_dict['train_step'] = self.step
                    self.temp_dict['loss_train'] = ret.get("value_loss")
                elif ret.get('name') == 'Test':
                    self.temp_dict['test_step'] = self.step
                    self.temp_dict['loss_test'] = ret.get("value_loss")

            elif ret.get("value_accuracy"):
                # print ret.get("value_accuracy")
                if ret.get('name') == "Train":
                    self.temp_dict['train_step'] = self.step
                    self.temp_dict['accuracy_train'] = ret.get("value_accuracy")
                elif ret.get('name') == 'Test':
                    # print ret.get('name') == 'Test'
                    self.temp_dict['test_step'] = self.step
                    self.temp_dict['accuracy_test'] = ret.get("value_accuracy")
                    # print self.temp_dict
                else:
                    self.temp_dict['accuracy_train'] = 0
            elif ret.get("value_loss_bbox"):
                if ret.get('name') == "Train":
                    self.temp_dict['train_step'] = self.step
                    self.temp_dict['train_loss_bbox'] = ret.get("value_loss_bbox")
                elif ret.get('name') == 'Test':
                    self.temp_dict['test_step'] = self.step
                    self.temp_dict['test_loss_bbox'] = ret.get("value_loss_bbox")
            elif ret.get("value_loss_coverage"):
                if ret.get('name') == "Train":
                    self.temp_dict['train_step'] = self.step
                    self.temp_dict['train_loss_coverage'] = ret.get("value_loss_coverage")
                elif ret.get('name') == 'Test':
                    self.temp_dict['test_step'] = self.step
                    self.temp_dict['test_loss_coverage'] = ret.get("value_loss_coverage")
            elif ret.get("value_mAP"):
                self.temp_dict['test_step'] = self.step
                self.temp_dict['mAP'] = ret.get("value_mAP")
            elif ret.get("value_precision"):
                self.temp_dict['test_step'] = self.step
                self.temp_dict['precision'] = ret.get("value_precision")
            elif ret.get("value_recall"):
                self.temp_dict['test_step'] = self.step
                self.temp_dict['recall'] = ret.get("value_recall")
            else:
                pass
        else:
            pass
        if len(self.temp_dict) >= 2:
            # print("temp_dict: ", self.temp_dict)
            # print "socketio line: ", self.temp_dict
            self.graph_data_txt.write('%s\n' % self.temp_dict)
            self.graph_data_txt.flush()
            socketio.emit('task update',
                          {
                              'task': 'vip_job',
                              'update': 'accuracy_graph',
                              'data': self.temp_dict,
                          },
                          namespace='/jobs',
                          room=self.job_id,
                          )
            self.temp_dict = {}

        else:
            pass

    def get_output_line_parameter(self,line):
        """
        step,loss,lr made from 3 lines,per parameter per line
        I0329 06:59:55.182549 1 solver.cpp:334] Iteration 100 (497.307 iter/s, 0.197061s/98 iter), loss = 2.18689
        I0329 06:59:55.182579 1 solver.cpp:356] Train net output #0: loss = 2.18689 (* 1 = 2.18689 loss)
        I0329 06:59:55.182588 1 sgd_solver.cpp:161] Iteration 100, lr = 9.92565e-05, m = 0.9, wd = 0.0005, gs = 1

        :param line:
        :return:
        """
        float_exp = '(NaN|[-+]?[0-9]*\.?[0-9]+(e[-+]?[0-9]+)?)'

        # self.caffe_log.write('%s\n' % line)
        # self.caffe_log.flush()
        # parse caffe output
        timestamp, level, message = self.preprocess_output_caffe(line)
        if not message:
            return False
        # print("msg: ", message)

        # iteration updates,get step
        # Iteration 1700 (592.544 iter/s, 0.168764s/100 iter), loss = 0.398954
        # Train net output #0: loss = 0.398954 (* 1 = 0.398954 loss)
        # Iteration 1700, lr = 8.88916e-05, m = 0.9, wd = 0.0005, gs = 1
        match = re.match(r'Iteration (\d+)', message)
        if match:
            step = int(match.group(1))
            step = "%s.0" % (step)
            # step = float(step)
            # print("step: ", step)
            step = str(step)
            return {"step": step}

        # net output,get loss
        # Train net output  # 0: loss = 2.40894 (* 1 = 2.40894 loss)
        # match = re.search(r'(Train|Test) net output #(\d+): (\S*) = (\d+.\d+)', message, flags=re.IGNORECASE)
        match = re.search(r'(Train|Test) net output #(\d+): (loss) = (\d+.\d+|\d+)', message, flags=re.IGNORECASE)
        if match:
            name = match.group(1)
            name_loss = match.group(3)
            value_loss = match.group(4)
            # print "%s = %s: " % (name_loss, value_loss)
            value_loss = str(value_loss)
            return {"value_loss": value_loss, "name": name}

        match = re.search(r'(Train|Test) net output #(\d+): (accuracy) = (\d+.\d+|\d+)', message, flags=re.IGNORECASE)
        if match:
            name = match.group(1)
            name_accuracy = match.group(3)
            value_accuracy = match.group(4)

            value_accuracy = str(value_accuracy)
            # print "%s = /%s: " % (name_accuracy, value_accuracy)
            return {"value_accuracy": value_accuracy, "name": name}

        # learning rate updates
        match = re.match(r'Iteration (\d+).*lr = %s' % float_exp, message, flags=re.IGNORECASE)
        if match:
            step = int(match.group(1))
            lr = float(match.group(2))
            # print("lr :", lr)
            return {"lr": lr}

        match = re.search(r'(Train|Test) net output #(\d+): (loss_bbox) = (\d+.\d+|\d+)', message, flags=re.IGNORECASE)
        if match:
            name = match.group(1)
            name_loss_bbox = match.group(3)
            value_loss_bbox = match.group(4)
            # print "%s = /%s: " % (name_accuracy, value_accuracy)
            value_loss_bbox = float(value_loss_bbox) * 2
            value_loss_bbox = str(value_loss_bbox)
            return {"value_loss_bbox": value_loss_bbox, "name": name}

        match = re.search(r'(Train|Test) net output #(\d+): (loss_coverage) = (\d+.\d+|\d+)', message, flags=re.IGNORECASE)
        if match:
            name = match.group(1)
            name_loss_coverage = match.group(3)
            value_loss_coverage = match.group(4)
            # print "%s = /%s: " % (name_accuracy, value_accuracy)
            value_loss_coverage = str(value_loss_coverage)
            return {"value_loss_coverage": value_loss_coverage, "name": name}

        match = re.search(r'(Train|Test) net output #(\d+): (mAP) = (\d+.\d+|\d+)', message, flags=re.IGNORECASE)
        if match:
            name = match.group(1)
            name_mAP = match.group(3)
            value_mAP = match.group(4)
            # print "%s = /%s: " % (name_accuracy, value_accuracy)
            value_mAP = str(value_mAP)
            return {"value_mAP": value_mAP, "name": name}

        match = re.search(r'(Train|Test) net output #(\d+): (precision) = (\d+.\d+|\d+)', message, flags=re.IGNORECASE)
        if match:
            name = match.group(1)
            name_precision = match.group(3)
            value_precision = match.group(4)
            # print "%s = /%s: " % (name_accuracy, value_accuracy)
            value_precision = str(value_precision)
            return {"value_precision": value_precision, "name": name}

        match = re.search(r'(Train|Test) net output #(\d+): (recall) = (\d+.\d+|\d+)', message, flags=re.IGNORECASE)
        if match:
            name = match.group(1)
            name_recall = match.group(3)
            value_recall = match.group(4)
            # print "%s = /%s: " % (name_accuracy, value_accuracy)
            value_recall = str(value_recall)
            return {"value_recall": value_recall, "name": name}

    def preprocess_output_caffe(self,line):

        # NOTE: This must change when the logging format changes
        # LMMDD HH:MM:SS.MICROS pid file:lineno] message
        # "I0329 07:00:07.661504 1 sgd_solver.cpp:161] Iteration 6800, lr = 6.7767e-05, m = 0.9, wd = 0.0005, gs = 1 "
        # "I0329 07:00:07.830659 1 solver.cpp:334] Iteration 6900 (591.021 iter/s, 0.169199s/100 iter), loss = 0.214692"
        # "I0329 07:00:07.830698 1 solver.cpp:356] Train net output #0: loss = 0.214692 (* 1 = 0.214692 loss)"
        match = re.match(r'(\w)(\d{4} \S{8}).*]\s+(\S.*)$', line)
        if match:
            level = match.group(1)
            if level == 'I':
                level = 'info'
            elif level == 'W':
                level = 'warning'
            elif level == 'E':
                level = 'error'
            elif level == 'F':  # FAIL
                level = 'critical'

            # add the year because caffe omits it
            timestr = '%s%s' % (time.strftime('%Y'), match.group(2))
            message = match.group(3)

            timestamp = time.mktime(time.strptime(timestr, '%Y%m%d %H:%M:%S'))
            return (timestamp, level, message)
        else:
            return (None, None, None)


    def modification_file(self, file_test_path):
        base_path = self.base_path
        # print "file_path %s",base_path
        new_path = base_path.split("code")[0]
        # base_path = self.base_path
        # print "basepase %s", base_path
        new_file_path = os.path.join(new_path, '{}'.format(self.model_dir+'/'+'slover_new.prototxt'))
        # print new_file_path
        with open(base_path, mode='r+') as r_file:
            with open(new_file_path, 'w+') as w_file:
                for line in r_file.readlines():
                    # print('*** ', line)
                    if line.find("$net$") >= 0:
                        new_line = line.replace("$net$",  '"'+file_test_path+'"')
                        w_file.write(new_line)
                    elif line.find("$snapshot_prefix$") >= 0:
                        new_line = line.replace("$snapshot_prefix$", '"'+self.model_dir+'/"')
                        w_file.write(new_line)
                    else:
                        w_file.write(line)
        return new_file_path

    def modification_test_file(self):
        file_path = self.file_path
        # print "basepase %s", file_path
        train_dir = self.train_dir
        # print "train_dir %s",train_dir
        test_dir = self.test_dir
        # print "test_dir %s", test_dir
        new_path = file_path.split("code")[0]
        new_file_path = os.path.join(new_path, '{}'.format(self.model_dir+'/'+'train_val_new.prototxt'))
        # print new_file_path
        with open(file_path, mode='r+') as r_file:
            with open(new_file_path, 'w+') as w_file:
                for line in r_file.readlines():
                    # print('*** ', line)
                    if line.find("$train$") >= 0:
                        new_line = line.replace("$train$",  '"'+train_dir+'"')
                        w_file.write(new_line)
                    elif line.find("$test$") >= 0:
                        new_line = line.replace("$test$", '"'+test_dir+'"')
                        w_file.write(new_line)
                    else:
                        w_file.write(line)
        return new_file_path



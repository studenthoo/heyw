#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-2017, NVIDIA CORPORATION.  All rights reserved.
from __future__ import absolute_import

import re
import os
import subprocess
import gevent
import hyperai
import time
from hyperai.config import config_value
from hyperai.utils import read_process_stdout


class Monitor:

    def __init__(self, job):
        self.job = job
        self.res = None
        self.mem = None
        self.mem_total = None

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
                        data_cpu['mem_pct'] = data_cpu['mem_used'] / data_cpu['men_total']
                if cpu_res['cpu']:
                    data_cpu['cpu_pct'] = cpu_res['cpu']['us']
            else:
                data_cpu = {'cpu_pct': 0, 'pid': 0, 'mem_pct': 0, 'mem_used': 0}

            data_gpu = []
            self.res = self.get_gpu_msg(pod_name)
            # res = self.other_message()
            res = self.res
            if res:
                for each in res:
                    if 'container_name' not in each:
                        each['container_name'] = "None"
                    container_list = []
                    update = {}
                    for key, val in each.items():
                        if key != 'container_name':
                            if each[key]['name'] and each[key]['utilization'] and each[key]['memory'] and each[key][ 'temperature']:
                                update = {'name': each[key]['name'],
                                          'index': key,
                                          'temperature': each[key]['temperature'],
                                          'memory': each[key]['memory'],
                                          'utilization': each[key]['utilization']}

                                update.update(each[key])
                                # update['other'] = each['other']
                                container_list.append(update)

                    data_gpu.append({'container_name': each['container_name'], 'value': container_list})
            with app.app_context():
                data = {'data_gpu': data_gpu, 'data_cpu': data_cpu}
                # print '==============>', data
                socketio.emit('task update',
                              {
                                  'task': 'monitor',
                                  'update': 'gpu_utilization',
                                  'data': data,
                              },
                              room=self.job.id(),
                              namespace='/jobs',
                              )
            gevent.sleep(1)

    def exec_command(self, command, symbool=None):
        if symbool:
            command = "sudo {}".format(command)
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        return read_process_stdout(p)
        # res = p.stdout.read()
        # return res

    def get_gpu_msg(self, pod_base_name):
        get_pods_command = "kubectl get po -o wide"
        for i in range(10):
            res1 = self.exec_command(get_pods_command)
            if res1:
                full_pod_name_list = self.get_full_pod_name(res1, pod_base_name)
                if full_pod_name_list is not None and len(full_pod_name_list) > 0:
                    time.sleep(1)
                    get_gpu_from_pod_list = self.get_gpu_from_pod(full_pod_name_list)
                    return get_gpu_from_pod_list
            else:
                pass

    def parse_gpu_msg(self, lines=None):
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
            device_query_file = os.path.join(config_value('jobs_dir'), 'public', 'device_query.py')
            get_gpu_from_pod = "kubectl exec {} python {}".format(pod, device_query_file)

            if self.job.framework == 'pytorch':
                get_gpu_from_pod = "kubectl exec {} /usr/bin/python {}".format(pod, device_query_file)
            res2 = self.exec_command(get_gpu_from_pod)
            if res2:
                res = self.parse_gpu_msg(res2)
                res['container_name'] = pod
                gpu_msg_list.append(res)
            else:
                pass
        return gpu_msg_list  # [[{1}, {2}, ...], [{1}, {2}, ...], ...]

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


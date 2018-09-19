# coding=utf-8
import os
import subprocess
import hyperai
import yaml
import time

from hyperai.config import config_value
from kubernetes import client, config
from hyperai.config import config_value
from hyperai.utils import read_process_stdout
import re


class KubernetasCoord(object):
    def __init__(self, logger, **kwargs):
        self.logger = logger
        config.load_kube_config()
        self.v1 = client.CoreV1Api()

        self.job_id = kwargs['job_id']
        self.job_dir = kwargs['job_dir']
        self.task_obj = kwargs['task_obj']

        self.image = kwargs['image']
        self.args = kwargs['args']
        self.node_count = kwargs.pop('node', 1)
        self.cpu_count = kwargs.pop('cpu', 4)
        self.gpu_count = kwargs.pop('gpu', 1)
        self.memory_count = kwargs.pop('memory', 8)

    def __repr__(self):
        return "pod_name[%s] cpu[%s] gpu[%s] memory[%s] node[%s]" \
               % (self.get_pod_name(self.job_id), self.cpu_count,
                  self.gpu_count, self.memory_count, self.node_count)

    @staticmethod
    def get_pod_name(job_id):
        return "%s-%s" % (config_value('creater'), job_id)

    def get_pods_status(self, pod_label):
        """
        get pod status
        :param job_id:
        :return:
        """
        resp = self.v1.list_namespaced_pod(namespace='default', label_selector='app=%s' % pod_label)
        status_list = []
        for i in resp.items:
            status_list.append(i.status.phase)
        return status_list

    @staticmethod
    def generate_yaml(job_id, job_dir, pod_label, **kwargs):
        gpu_count = kwargs['gpu_count']
        cpu_count = kwargs['cpu_count']
        node_count = kwargs['node_count']
        command = kwargs['command']
        argument = kwargs['argument']
        # print "node_count: ",node_count
        image = kwargs['image']
        select_node = kwargs['select_node']
        memory_count = kwargs['memory_count']

        matchExpressions_values = kwargs['matchExpressions_values']
        matchExpressions_values = '[%s]' % str(matchExpressions_values)
        hyperai_path = os.path.dirname(hyperai.__file__)
        # base_yaml_path = os.path.join(hyperai_path, 'tools/k8s/mpi_node_base.yaml')
        if gpu_count > 0:
            base_yaml_path = config_value('au_gpu_mpi_base_yaml')
        else:
            base_yaml_path = config_value('mpi_base_yaml')

        new_yaml_path = os.path.join(job_dir, '{}.yaml'.format(job_id))
        name = pod_label

        with open(base_yaml_path, mode='r+') as r_file:
            with open(new_yaml_path, 'w+') as w_file:
                for line in r_file.readlines():
                    # print('*** ', line)
                    if line.find("$name$") >= 0:
                        new_line = line.replace("$name$", name)
                        w_file.write(new_line)
                    elif line.find("$label$") >= 0:
                        new_line = line.replace("$label$", name)
                        w_file.write(new_line)
                    elif line.find("$select_node$") >= 0:
                        new_line = line.replace("$select_node$", select_node)
                        w_file.write(new_line)
                    elif line.find("$image$") >= 0:
                        new_line = line.replace("$image$", image)
                        w_file.write(new_line)
                    elif line.find("$node_count$") >= 0:
                        new_line = line.replace("$node_count$", '%d'%(int(node_count)))
                        w_file.write(new_line)
                    elif line.find("$cpu$") >= 0:
                        new_line = line.replace("$cpu$", str(cpu_count))
                        w_file.write(new_line)
                    elif line.find("$gpu$") >= 0:
                        new_line = line.replace("$gpu$", str(gpu_count))
                        w_file.write(new_line)
                    elif line.find("$memory$") >= 0:
                        new_line = line.replace("$memory$", memory_count)
                        w_file.write(new_line)
                    elif line.find("$cmd$") >= 0:
                        new_line = line.replace("$cmd$", str(command))
                        w_file.write(new_line)
                    elif line.find("$args$") >= 0:
                        new_line = line.replace("$args$", str(argument))
                        w_file.write(new_line)
                    elif line.find("$nfsip$") >= 0:
                        new_line = line.replace("$nfsip$", config_value('nfs_ip'))
                        w_file.write(new_line)
                    elif line.find("$nfspath$") >= 0:
                        new_line = line.replace("$nfspath$", config_value('nfs_path'))
                        w_file.write(new_line)
                    elif line.find("$matchExpressions-values$") >= 0:
                        new_line = line.replace("$matchExpressions-values$", matchExpressions_values)
                        w_file.write(new_line)
                    else:
                        w_file.write(line)
        return new_yaml_path

    def create_deployment(self, yaml_path, pod_label):
        with open(yaml_path) as f:
            dep = yaml.load(f)
            resp = client.ExtensionsV1beta1Api().create_namespaced_deployment(body=dep, namespace="default")
            self.logger.info("Deployment created. status='%s'" % str(resp.status))
        running = False
        tem_res_list = []
        start_time = time.time()  # +++2018-8-24
        while not running:
            time.sleep(1)
            status = self.get_pods_status(pod_label=pod_label)
            if len(status) > 0:
                # self.logger.info(status)
                running = True
                for i, stat in enumerate(status):
                    if stat == 'Running':
                        if i not in tem_res_list:
                            self.logger.info('Pod Status: %s' % status)  # +++2018-8-24
                            tem_res_list.append(i)
                            self.task_obj.logger.info(
                                "Running pod list = %s ; The NUM of append pod to Running list = <%d>" % (
                                tem_res_list, i))
                            self.task_obj.pre_allocate_res_task()
                    elif not stat == 'Running':
                        running = False
                        continue
                    if time.time() - start_time > 20:  # +++2018-8-24
                        self.logger.info('Pod Status: %s' % status)  # +++2018-8-24
                        start_time = time.time()  # +++2018-8-24

        self.logger.info("Deployment created successfully!")

    @staticmethod
    def delete_deployment(name):
        # Delete deployment
        api_response = client.ExtensionsV1beta1Api().delete_namespaced_deployment(
            name=name,
            namespace="default",
            body=client.V1DeleteOptions(
                propagation_policy='Foreground',
                grace_period_seconds=5))
        print("Deployment deleted. status='%s'" % str(api_response.status))

    def generate_hostfile(self, pod_label, slots, job_dir):
        resp = self.v1.list_namespaced_pod(namespace='default', label_selector='app=%s' % pod_label)
        lines = []
        for i in resp.items:
            lines.append('%s slots=%d' % (i.status.pod_ip, int(slots)))
        hostfile_path = os.path.join(job_dir, 'hostfile')
        f = open(hostfile_path, 'w')
        lines = [line + '\n' for line in lines]
        f.writelines(lines)
        f.close()

    def container_prepare(self, job_id):
        self.node_count = 1
        pod_label = self.get_pod_name(job_id)
        self.command = [str(self.args[0])]
        self.argument = self.args[1:]
        if not self.memory_count.endswith("Gi"):
            memory_count = "%s%s" % (self.memory_count, "Gi")
        else:
            memory_count = self.memory_count
        print memory_count
        yaml_path = self.generate_yaml(job_id=job_id,
                                       job_dir=self.job_dir,
                                       pod_label=pod_label,
                                       node_count=self.node_count,
                                       gpu_count=self.gpu_count,
                                       cpu_count=self.cpu_count,
                                       memory_count=memory_count,
                                       select_node="node02",
                                       image=self.image,
                                       command=self.command,
                                       argument=self.argument,
                                       matchExpressions_values=self.task_obj.node_label,
                                       )
        print("Create New_yaml Successed.")
        self.create_deployment(yaml_path, pod_label=pod_label)
        self.generate_hostfile(pod_label=pod_label, slots=self.gpu_count, job_dir=self.job_dir)
        return self.get_full_pod_name(pod_label=pod_label)

    @staticmethod
    def delete_pods(job_id):
        KubernetasCoord.delete_deployment(name=KubernetasCoord.get_pod_name(job_id))

    def get_full_pod_name(self,pod_label):
        resp = self.v1.list_namespaced_pod(namespace='default', label_selector='app=%s' % pod_label)
        for i in resp.items:
            full_pod_name_path = i.metadata.self_link
            base_dir, full_pod_name = os.path.split(full_pod_name_path)
        # print("full_pod_name: ",full_pod_name)
        return full_pod_name

    @staticmethod
    def parse_pod_msg(element, content):
        one_pattern = re.compile(r'(\S*{}\S*)\s*(\S+)\s*(\S+)\s*(\S+)\s*(\S+)\s*(\S+)\s*(\S+)\s*'.format(element))
        all_find_list = re.findall(one_pattern, content)
        if all_find_list:
            # return [all_find_list.group(1), all_find_list.group(2), all_find_list.group(3)]
            return all_find_list
        else:
            return None
        pass

    @staticmethod
    def short_exec_com(command="kubectl get po -a -o wide"):
        p = subprocess.Popen(args=command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        return read_process_stdout(p)



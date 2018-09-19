# coding=utf-8
import os
import subprocess
import hyperai
import yaml
import time

from hyperai.config import config_value
from kubernetes import client, config
from hyperai.config import config_value


class KubernetasCoord(object):

    def __init__(self, logger, output_log, **kwargs):
        self.logger = logger
        self.output_log = output_log
        config.load_kube_config()
        self.v1 = client.CoreV1Api()

        self.task_obj = kwargs['task_obj']
        self.job_id = kwargs['job_id']
        self.job_dir = kwargs['job_dir']
        self.node_count = kwargs.pop('node', 1)
        self.cpu_count = kwargs.pop('cpu', 4)
        self.gpu_count = kwargs.pop('gpu', 1)
        self.memory_count = kwargs.pop('memory', 8)
        # self.node_label = kwargs.pop('node_label', None)

    def __repr__(self):
        return "pod_name[%s] cpu[%s] gpu[%s] memory[%s] node[%s]" \
               % (self.get_pod_name(self.job_id), self.cpu_count,
                  self.gpu_count, self.memory_count, self.node_count)

    @staticmethod
    def get_pod_name(job_id):
        return "%s-%s" % (config_value('creater'), job_id)

    def get_pods_status(self, pod_label):
        """
        根据job_id获取pod状态信息
        :param job_id:
        :return:
        """
        s_time = time.time()
        # print("\n* * [BF] * * ")
        resp = self.v1.list_namespaced_pod(namespace='default', label_selector='app=%s' % pod_label)
        # print(resp)
        # print("* * [AF] * * time=%s" % (time.time()-s_time))
        status_list = []
        for i in resp.items:
            status_list.append(i.status.phase)
        return status_list

    @staticmethod
    def generate_yaml(job_id, job_dir, pod_label, **kwargs):
        matchExpressions_values = '[%s]' % kwargs['matchExpressions_values']
        gpu_count = kwargs['gpu_count']
        cpu_count = kwargs['cpu_count']
        node_count = kwargs['node_count']
        image = kwargs['image']
        select_node = kwargs['select_node']
        if not str(kwargs['memory_count']).endswith("Gi"):
            memory_count = "%s%s" % (kwargs['memory_count'], "Gi")
        else:
            memory_count = kwargs['memory_count']
        hyperai_path = os.path.dirname(hyperai.__file__)
        if gpu_count > 0:
            base_yaml_path = config_value('gpu_mpi_base_yaml')
        else:
            base_yaml_path = config_value('mpi_base_yaml')

        new_yaml_path = os.path.join(job_dir, '{}.yaml'.format(job_id))
        nfspath = config_value('nfs_path')
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
                        new_line = line.replace("$node_count$", '%d' % node_count)
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
                    elif line.find("$nfsip$") >=0:
                        new_line = line.replace("$nfsip$",config_value('nfs_ip'))
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
            self.output_log.write("Deployment created. status='%s' \n" % str(resp.status))
            self.logger.info("Deployment created. status='%s'" % str(resp.status))
        running = False
        start_time = time.time()  # +++2018-8-24
        tem_res_list = []
        while not running:
            time.sleep(1)
            status = self.get_pods_status(pod_label=pod_label)
            if self.task_obj.aborted.is_set():
                KubernetasCoord.delete_pods(self.job_id)
                print ("Del Pod Successed .")
                self.output_log.write('Del Pod Successed : %s \n' % status)
                self.logger.info('Del Pod Successed : %s' % status)
                return False
            if len(status) > 0:
                # self.logger.info("Pod Status:  %s" % status)
                running = True
                for i, stat in enumerate(status):
                    if stat == 'Running':
                        if i not in tem_res_list:
                            self.logger.info('Pod Status: %s' % status)  # +++2018-8-24
                            tem_res_list.append(i)
                            self.task_obj.pre_allocate_res_task()
                            self.output_log.write("Success to allocate resource. \n")
                    elif not stat == 'Running':
                        running = False
                        continue

                    if time.time() - start_time > 20:  # +++2018-8-24
                        self.logger.info('Pod Status: %s' % status)  # +++2018-8-24
                        start_time = time.time()  # +++2018-8-24
        self.logger.info("Deployment created successfully!")
        self.output_log.write("----*----Deployment created successfully!----*---- \n")
        return True

    @staticmethod
    def delete_deployment(name):
        # Delete deployment
        api_response = client.ExtensionsV1beta1Api().delete_namespaced_deployment(
            name=name,
            namespace="default",
            body=client.V1DeleteOptions(
                propagation_policy='Foreground',
                grace_period_seconds=5))
        print("\nDeployment deleted. status='%s'" % str(api_response.status))

    def generate_hostfile(self, pod_label, slots, job_dir):
        resp = self.v1.list_namespaced_pod(namespace='default', label_selector='app=%s' % pod_label)
        lines = []
        for i in resp.items:
            lines.append('%s slots=%d' % (i.status.pod_ip, slots))
        hostfile_path = os.path.join(job_dir, 'hostfile')
        f = open(hostfile_path, 'w')
        lines = [line + '\n' for line in lines]
        f.writelines(lines)
        f.close()

    def container_prepare(self, job_id):
        pod_label = self.get_pod_name(job_id)
        self.pod_label = pod_label
        yaml_path = self.generate_yaml(job_id=job_id, job_dir=self.job_dir, pod_label=pod_label,
                                       node_count=self.node_count,
                                       gpu_count=self.gpu_count,
                                       cpu_count=self.cpu_count,
                                       memory_count=self.memory_count,
                                       select_node="node03",
                                       image=config_value('image_list')['mpi_image'],
                                       matchExpressions_values=self.task_obj.node_label,
                                       )
        print("Create New_yaml Successed.")
        self.output_log.write("----*----Create New_yaml Successed.----*---- \n")
        self.create_deployment(yaml_path, pod_label=pod_label)
        self.generate_hostfile(pod_label=pod_label, slots=self.gpu_count, job_dir=self.job_dir)
        return True

    def get_full_pod_name(self):
        pod_label = self.pod_label
        resp = self.v1.list_namespaced_pod(namespace='default', label_selector='app=%s' % pod_label)
        for i in resp.items:
            full_pod_name_path = i.metadata.self_link
            base_dir, full_pod_name = os.path.split(full_pod_name_path)
            if full_pod_name:
                return full_pod_name
        return None

    @staticmethod
    def delete_pods(job_id):
        KubernetasCoord.delete_deployment(name=KubernetasCoord.get_pod_name(job_id))


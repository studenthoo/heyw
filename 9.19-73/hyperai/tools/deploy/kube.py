# coding=utf-8
import os
import subprocess
import hyperai
import yaml
import time
import subprocess
import platform
import shutil
import re
from hyperai.config import config_value
from kubernetes import client, config
from hyperai.config import config_value
from hyperai.tools.kuber.kube import ManageKubernets as k8s
from hyperai.utils import read_process_stdout


class KubernetasCoord(object):
    def __init__(self, logger, **kwargs):
        self.logger = logger
        config.load_kube_config()
        self.v1 = client.CoreV1Api()

        # self.mode = kwargs['mode']
        self.job_id = kwargs['job_id']
        self.job_dir = kwargs['job_dir']

        self.image = kwargs['image']
        # self.framework = kwargs['framework']
        self.args = kwargs['args']
        # self.node_count = kwargs.pop('node', 1)
        self.cpu_count = kwargs.pop('cpu', 4)
        self.gpu_count = kwargs.pop('gpu', 1)
        self.memory_count = kwargs.pop('memory', 8)
        self.optimization_engine = kwargs['optimization_engine']
        self.command = kwargs.pop('command', None)
        # self.yaml_path = None
        self.replicas = kwargs['replicas']
        self.nodePort = kwargs['nodePort']
        self.label_name = kwargs['label_name']

    def __repr__(self):
        return "pod_name[%s] cpu[%s] gpu[%s] memory[%s] node[%s]" \
               % (self.get_pod_name(self.job_id), self.cpu_count,
                  self.gpu_count, self.memory_count, self.node_count)

    @staticmethod
    def get_pod_name(job_id):
        return "%s-%s" % (config_value('creater'), job_id)

    @staticmethod
    def generate_yaml(job_id, job_dir, pod_label, **kwargs):
        gpu_count = kwargs['gpu_count']
        cpu_count = kwargs['cpu_count']
        # node_count = kwargs['node_count']
        command = kwargs['command']
        argument = kwargs['argument']
        # print "node_count: ",node_count
        image = kwargs['image']
        replicas = kwargs['replicas']
        nodePort = kwargs['nodePort']
        args = kwargs['args']
        label_name = "[" + kwargs['label_name'] + ']'
        # select_node = kwargs['select_node']
        optimization_engine = kwargs['optimization_engine']
        if not str(kwargs['memory_count']).endswith("Gi"):
            memory_count = "%s%s" % (kwargs['memory_count'], "Gi")
        else:
            memory_count = kwargs['memory_count']
        hyperai_path = os.path.dirname(hyperai.__file__)
        if optimization_engine == 'TensorRT':
            base_yaml_path = config_value('tensorrt_yaml')
        elif optimization_engine == 'TF-serving':
            base_yaml_path = config_value('tfserving_yaml')
        # if gpu_count > 0:
        #     base_yaml_path = config_value('')
        # else:
        #     base_yaml_path = config_value('mpi_base_yaml')

        new_yaml_path = os.path.join(job_dir, '{}.yaml'.format(job_id))
        name = pod_label
        nfs_path = config_value("nfs_path")
        hyperai_root = config_value('hyperai_root')

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
                    elif line.find("$replicas$") >= 0:
                        new_line = line.replace("$replicas$", '%d' % (int(replicas)))
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
                        new_line = line.replace("$args$", str(args))
                        w_file.write(new_line)
                    elif line.find("$nodePort") >= 0:
                        new_line = line.replace("$nodePort$", '%d' % (int(nodePort)))
                        w_file.write(new_line)
                    elif line.find("$externalIPs$") >= 0:
                        new_line = line.replace("$externalIPs$", config_value('deploy_ip'))
                        w_file.write(new_line)
                    elif line.find("$nfsip$") >= 0:
                        new_line = line.replace("$nfsip$", config_value('nfs_ip'))
                        w_file.write(new_line)
                    elif line.find("$nfspath$") >= 0:
                        new_line = line.replace("$nfspath$", config_value('nfs_path'))
                        w_file.write(new_line)
                    elif line.find("$matchExpressions-values$") >= 0:
                        new_line = line.replace("$matchExpressions-values$",label_name)
                        w_file.write(new_line)
                    else:
                        w_file.write(line)
        return new_yaml_path

    @classmethod
    def exe_command(cls, command=None):
        if isinstance(command, str):
            # print 'start exec 11'
            p = subprocess.Popen(command,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 close_fds=False if platform.system() == 'Windows' else True,
                                 shell=True)
            return read_process_stdout(p)
            # print 'execing 22'
            # logger.warning("End and the command is: %s" % kwargs['command'])
            # this_output = p.stdout.read()
            # print this_output,'333'
            # print this_output
            # logger.warning("The command is: %s"% (kwargs['command']))
            # logger.warning("The result is: %s"% (this_output))
            # return this_output
        raise ValueError("Not get command to exe.")
        pass

    def create_deployment(self, yaml_path, pod_label):
        # print 666666666666,yaml_path
        command = "kubectl create -f {} --validate=false".format(yaml_path)
        # print 777777777
        try:
            p = self.exe_command(command)
            print p, 'create deployment'
        except Exception as e:
            print e
            return
        # print a
        self.logger.info("Deployment created successfully!")

    # @staticmethod
    # def delete_deployment(name):
    #     # Delete deployment
    #     api_response = client.ExtensionsV1beta1Api().delete_namespaced_deployment(
    #         name=name,
    #         namespace="default",
    #         body=client.V1DeleteOptions(
    #             propagation_policy='Foreground',
    #             grace_period_seconds=5))
    #     print("Deployment deleted. status='%s'" % str(api_response.status))
    @classmethod
    def delete_by_yaml(cls, yaml_path):
        # 根据yaml文件删除,创建k8s实例的时候已经指定了yaml文件
        if yaml_path:
            return "kubectl delete -f {}".format(yaml_path)
        # self.logger.info("No appropriate file to delete the pod.")

    @classmethod
    def delete_deployment(cls, yaml_path):
        command = cls.delete_by_yaml(yaml_path)
        dirname, filename = os.path.split(yaml_path)
        # print dirname,filename,'2222222222222222'
        try:
            p = cls.exe_command(command)
            print p
            shutil.rmtree(dirname)
        except Exception as e:
            print e
            return
        # self.logger.info("Deployment deleted successfully!")
        print "Deployment {} deleted successfully!".format(yaml_path)

    @classmethod
    def delete_svc(cls, job_id):
        svc_name = "{}-{}".format(config_value('creater'), job_id)
        cmd = 'kubectl delete svc {}'.format(svc_name)
        try:
            cls.exe_command(cmd)
        except Exception as e:
            print e

        print 'Service {} deleted successfully!'.format(svc_name)

    def container_prepare(self, job_id, optimization_engine):
        pod_label = self.get_pod_name(job_id)
        if optimization_engine == 'TensorRT':
            command = self.command
            self.argument = None
        elif optimization_engine == 'TF-serving':
            command = '["sh","-c"]'
            self.argument = self.args
        # self.command = ['/usr/sbin/sshd']
        # self.argument = ['-D']
        # 生成yaml脚本
        yaml_path = self.generate_yaml(
            job_id=job_id,
            job_dir=self.job_dir,
            pod_label=pod_label,
            gpu_count=self.gpu_count,
            cpu_count=self.cpu_count,
            memory_count=self.memory_count,
            image=self.image,
            args=self.args,
            command=command,
            argument=self.argument,
            optimization_engine=optimization_engine,
            replicas=self.replicas,
            nodePort=self.nodePort,
            label_name=self.label_name,
        )
        # self.yaml_path = yaml_path
        # print("Create New_yaml Successed.",yaml_path)
        self.create_deployment(yaml_path, pod_label=pod_label)
        # print '333333333333333'
        full_pod_name = self.get_full_pod_name(pod_label=pod_label)
        return full_pod_name
        # self.generate_hostfile(pod_label=pod_label, slots=self.gpu_count, job_dir=self.job_dir)
        # if self.framework != "tensorflowmpi":
        #     return self.get_full_pod_name(pod_label=pod_label) # 返回pod名字

    @staticmethod
    def parse_pod_name(element, content):
        return re.findall(r'\S*{}\S*'.format(element), content)
        # return re_findall_list

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
        # return p.stdout.read()

    def get_full_pod_name(self, pod_label):
        resp = self.v1.list_namespaced_pod(namespace='default', label_selector='app=%s' % pod_label)
        for i in resp.items:
            full_pod_name_path = i.metadata.self_link
            base_dir, full_pod_name = os.path.split(full_pod_name_path)
        # print("full_pod_name: ",full_pod_name)
        return full_pod_name

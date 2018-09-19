# !/usr/bin/python
# -*- encoding: utf-8 -*-

import re
import sys
import os
import subprocess


class ManageKubernets(object):
    """
    管理kubernets
    执行相应的kubectl命令
    """
    def __init__(self, yaml_file, pod_name, replicas=1):
        # 依据给定的yaml文件，初始化一个实例
        self.yaml_file = yaml_file
        self.pod_name = pod_name
        self.replicas = str(replicas)
        self.command_path = "/usr/bin/kubectl"
        self.validate = False
        self.pod_type = ['rc', 'job', 'pod', 'service', 'deployment']
        pass

    def __str__(self):
        return "the yaml_file is {}".format(self.yaml_file)
        pass

    def ssh_kube(self, username, ip, port, password=None):
        # 远程连接master节点
        return "ssh -p {} {}@{}".format(port, username, ip)
        pass

    def create_pods(self, yaml_file=None, validate = False):
        # 创建新的pods：kubectl apply -f yaml
        if yaml_file:
            return "kubectl apply -f {} --validate=false".format(yaml_file)
        if self.yaml_file:
            return "kubectl apply -f {} --validate=false".format(self.yaml_file)
        print "No yaml_file to create the pod."
        raise ValueError("No yaml_file to create the pod.")

    @staticmethod
    def exe_distributed(pod_name=None,
                        file_path='/home/nfsdir/nfsdir/hyw/mnist1.py',
                        task_index=0, job_name=None,
                        ps_ip=None,
                        worker_ip=None,
                        index=None,
                        data_dir=None,
                        ):
        # 这里传过来的需要ip + port 端口可以随机生成
        if pod_name:
            return {'args': "kubectl exec {} -- python {} --task_index={} --job_name={} --parameter_servers={} "
                            "--worker={} --data_dir={}".format(pod_name, file_path, task_index, job_name, ps_ip, worker_ip, data_dir), 'index': index}
        print "No yaml_file"
        raise ValueError("No yaml_file to create pod")

    @staticmethod
    def exe_single(pod_name):
        if pod_name:
            return "kubectl logs -f {}".format(pod_name)
        raise ValueError('invalid pod_name')

    @staticmethod
    def env_init():
        return "source /etc/profile"


    def change_pods(self, replicas=None, pod_name=None):
        # 更改副本控制的数量 kubectl scale replicationcontroller --replicas=2 （pod_ name）
        if pod_name and replicas:
            return "kubectl scale replicationcontroller --replicas={} {}".format(replicas, pod_name)
        raise ValueError("Not specify the pod.")
        pass

    def delete_pods_all(self, force=False):
        # 删除所有的pods：kubectl delete pods –all
        if force:
            return "kubectl delete pods all -f"
        return "kubectl delete pods all"

    @staticmethod
    def delete_by_yaml(yaml=None):
        # 根据yaml文件删除,创建k8s实例的时候已经指定了yaml文件
        if yaml:
            return "kubectl delete -f {}".format(yaml)
        print "No appropriate file to delete the pod."

    def delete_pod_by_pod_id(self, pod_id):
        # 删除pod  kubectl delete -f yaml,不能彻底删除
        if pod_id:
            return "kubectl delete pod {}".format(pod_id)
        print "No pod_id."
        raise ValueError("Not exist the pod_id.")

    def delete_pods_by_pod_name(self, pod_type="rc", pod_name=None):
        # 通过pod类型删除pod : kubectl delete -f yaml
        if pod_type and pod_name:
            # res = self.get_pods_by_pod_type(pod_type)
            return "kubectl delete {} {}".format(pod_type, pod_name)
        if self.pod_name:
            return "kubectl delete {} {}".format(pod_type, self.pod_name)
        print "No pod_type."
        raise ValueError("Not find the pod %s of %s." % (pod_name, pod_type))
        pass

    @staticmethod
    # def cat_pods_all_by_pod_type(self, pod_type=None):
    def get_all_pods(detailed=True):
        # 获取所有的pod信息
        if detailed:
            return "kubectl get pod -o wide"
        else:
            return "kubectl get pod"
        pass

    @staticmethod
    def get_pods_by_pod_type(pod_type):
        # 获取指定类型的所有pod
        pod_type = str.lower(pod_type)
        if pod_type:
            # return "kubectl get {} -o wide".format(pod_type)
            return "kubectl get pod -a -o wide"
        print "No pod_id to get pods."
        return None
        pass

    def get_log_by_pod_name(self, pod_name):
        """
        find pod_name’log
        :param pod_name: 需要查看日志的pod_name（需要完整的pod_name）
        :return: 查看指定pod的日志记录的命令
        """
        if pod_name != self.pod_name:
            return "kubectl logs -f {}".format(pod_name)
        else:
            full_pod_name = self.get_full_pod_name(pod_base_name=pod_name)
            return "kubectl logs -f {}".format(full_pod_name)
        pass

    def get_mes_pod_field(self, pod_base_name=None, res=None):
        """
        获取指定pod的每个字段的信息
        :param
        res:通过使用 kubectl get po -o wide 命令获取的信息
        pod_name: 用户定义pod名
        :return dict type
        """
        data = {}
        # 处理输出的结果
        # pod_name_pattern = re.compile(r'{}.*?\s'.format(pod_base_name))
        pod_name_pattern = re.compile(r'{}'.format(pod_base_name))
        status_pattern = re.compile(r'[A-Z]+\w+')
        # ip_pattern = re.compile(r'172.22.\d+.\d+')
        ip_pattern = re.compile(r'\d+[.]\d+[.]\d+[.]\d+')
        node_pattern = re.compile(r'\w+')
        field_list = ["NAME", "READY", "STATUS", "RESTARTS", "AGE", "IP", "NODE"]
        if res:
            pod_list = res.split("\n")
        else:
            get_command = self.get_all_pods()
            res = self.exe_command(command=get_command)
            pod_list = res.split("\n")
        for li in pod_list:
            if pod_base_name:
                # 如果用户指定pod， 则获取指定pod的相关信息
                new_pod_name = re.search(pod_name_pattern, li)
                if new_pod_name:
                    full_pod_name = new_pod_name.group()
                    ip = re.search(ip_pattern, li)
                    if ip:
                        ip = ip.group()
                        # self.logger.info("ip:%s." % (ip))
                    else:
                        ip = "none"
                        # self.logger.info("IP is none")

                    node = re.search(node_pattern, li)
                    if node:
                        node = node.group()
                        # self.logger.info("node:%s." % (node))
                    else:
                        node = "none"
                    data[field_list[0]] = full_pod_name
                    data[field_list[2]] = status_pattern
                    data[field_list[5]] = ip
                    data[field_list[6]] = node
                else:
                    pass
            else:
                # 获取完整pod的信息
                # 多个空格替换为一个
                meta = {}
                pattern = re.compile(r'\s+')
                new_str = re.sub(pattern, ' ', li)
                if new_str.startswith("NAME"):
                    continue
                else:
                    new_li = new_str.split()
                    if len(new_li) > 0:
                        for i in range(len(new_li)):
                            meta[field_list[i]] = new_li[i]
                        data[meta[field_list[0]]] = meta
        return data

    def get_full_pod_name(self, res, pod_base_name):
        """

        :param pod_base_name:
        :param res: 
        :return: full_pod_name
        """
        # if pod_base_name:
        #     pattern = re.compile(r'{}.*?\s'.format(pod_base_name))
        # else:
        #     pattern = re.compile(r'{}.*?\s'.format(self.pod_name))
        print "the pod_base_name is:", pod_base_name

        # get full_pod_name by base_pod_name
        pattern = re.compile(r'{}\S*'.format(pod_base_name))
        if res:
            re_res = re.search(pattern, res)
            print "base_pod_name:full_pod_name,match_obj", re_res
            if re_res:
                full_pod_name = re_res.group()
                print "the full_pod_name is:", full_pod_name
                return full_pod_name
            else:
                return None
        pass

    def get_deployment(self):
        # 查看已有部署的容器kubectl get deployment
        return "kubectl get deployment"
        pass

    def desc_by_pod_name(self, pod_name=None):
        """
        根据用户传入的pod_name来获取详细的信息
        :param pod_name: 用户传入的pod_name（完整的pod_name）
        :return: 返回describe命令
        """
        # 查看指定pod的详细描述
        if pod_name != self.pod_name:
            return "kubectl describe pod {}".format(pod_name)

        # 如果用户传入的是用户定义的pod_name则先获取完整的pod_name
        full_pod_name = self.get_full_pod_name(pod_name)
        if full_pod_name:
            return "kubectl describe pod {}".format(full_pod_name)
        print "Don't get the describe because no full_pod_name."
        return None
        pass

    def desc_more_by_pod_name(self, pod_name=None):
        # 获取更为详细的信息 kubectl get pod pod_name -o wide
        if pod_name:
            return "kubectl get pod {} -o yaml".format(pod_name)
        if self.pod_name:
            return "kubectl get pod {} -o yaml".format(pod_name)
        return None
        pass

    def get_nodes(self, detailed=False):
        if detailed:
            return "kubectl get node -o wide"
        else:
            return "kubectl get node"
        pass

    def which_node(self, pod_name=None):
        # kubectl get pod pod_id -o wide
        if pod_name:
            return "kubectl get pod {} -o wide".format(pod_name)
        if self.pod_name:
            return "kubectl get pod {} -o wide".format(self.pod_name)
        print "No pod_name."
        return None
        pass
    pass

    def exe_command(self, command=None):
        if isinstance(command, str):
            p = subprocess.Popen(kwargs['command'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 close_fds=False if platform.system() == 'Windows' else True,
                                 cwd=base_dir,
                                 shell=True)
            # logger.warn("End and the command is: %s" % kwargs['command'])
            this_output = p.stdout.read()
            logger.warn("The command is >> ( %s ) << and the result is: \n %s"
                        % (kwargs['command'], this_output))
            return this_output
        raise ValueError("No command to exe.")
        pass
        pass


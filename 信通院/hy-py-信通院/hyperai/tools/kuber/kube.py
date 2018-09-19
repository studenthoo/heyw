# !/usr/bin/python
# -*- encoding: utf-8 -*-

import re
import sys
import os
import subprocess
from hyperai.utils import read_process_stdout


class ManageKubernets(object):
    """
    管理kubernets
    执行相应的kubectl命令
    """
    def __init__(self, generated_yaml_file_path, pod_name,logger,replicas=1):
        # 依据给定的yaml文件，初始化一个实例
        self.yaml_file = generated_yaml_file_path
        self.pod_name = pod_name
        self.replicas = str(replicas)
        self.command_path = "/usr/bin/kubectl"
        self.validate = False
        self.pod_type = ['rc', 'job', 'pod', 'service', 'deployment']
        self.logger = logger
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
        self.logger.info("No yaml_file to create the pod.")
        raise ValueError("No yaml_file to create the pod.")

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

    def delete_by_yaml(self, yaml=None):
        # 根据yaml文件删除,创建k8s实例的时候已经指定了yaml文件
        if yaml:
            return "kubectl delete -f {}".format(yaml)
        if self.yaml_file:
            return "kubectl delete -f {}".format(self.yaml_file)
        self.logger.info("No appropriate file to delete the pod.")
        # raise ValueError("No appropriate file to delete the pod.")

    def delete_pod_by_pod_id(self, pod_id):
        # 删除pod  kubectl delete -f yaml,不能彻底删除
        if pod_id:
            return "kubectl delete pod {}".format(pod_id)
        self.logger.info("No pod_id.")
        raise ValueError("Not exist the pod_id.")

    def delete_pods_by_pod_name(self, pod_type="rc", pod_name=None):
        # 通过pod类型删除pod : kubectl delete -f yaml
        if pod_type and pod_name:
            # res = self.get_pods_by_pod_type(pod_type)
            return "kubectl delete {} {}".format(pod_type, pod_name)
        if self.pod_name:
            return "kubectl delete {} {}".format(pod_type, self.pod_name)
        self.logger.info("No pod_type.")
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
            return "kubectl get {} -o wide".format(pod_type)
        self.logger.info("No pod_id to get pods.")
        return None
        pass

    @staticmethod
    def get_all_pods_status():
        # 获取指定类型的所有pod
        return "kubectl get pod -a -o wide"


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

    def get_msg_pod_field(self, base_pod_name=None, res=None):
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
        pod_name_pattern = re.compile(r'{}\S*'.format(base_pod_name))
        status_pattern = re.compile(r'[A-Z]+\w+')
        ip_pattern = re.compile(r'\d+[.]\d+[.]\d+[.]\d+')
        # ip_pattern = re.compile(r'172.\d+.\d+.\d+')
        node_pattern = re.compile(r'node\d+')
        field_list = ["NAME", "READY", "STATUS", "RESTARTS", "AGE", "IP", "NODE"]
        if res:
            pod_list = res.split("\n")
        else:
            get_command = self.get_all_pods_status()
            res = self.exe_command(command=get_command)
            pod_list = res.split("\n")

        for li in pod_list:
            # self.logger.info("li:%s"%(li))
            if base_pod_name:
                # 如果用户指定pod， 则获取指定pod的相关信息
                new_pod_name = re.search(pod_name_pattern, li)
                if new_pod_name:
                    full_pod_name = new_pod_name.group()
                    # self.logger.info("full_pod_name:%s."%(full_pod_name))

                    # pending/containercreating状态，ip和node为none,要做异常处理
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
                        # self.logger.info("Node is none.")

                    status = re.search(status_pattern, li).group()
                    # self.logger.info("status:%s."%(status))

                    data[field_list[0]] = full_pod_name
                    data[field_list[2]] = status
                    data[field_list[5]] = ip
                    data[field_list[6]] = node
                else:
                    full_pod_name = "none"
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

        self.logger.info("The pod info from resource list: %s"%(data))
        return data

    def get_msg_pod_field_list(self, job_id, res=None):
        """
        获取相同job_id的每个pod的信息
        :param
        res:通过使用 kubectl get po -o wide 命令获取的信息
        pod_name: 用户定义pod名
        :return contain dict type 's list
        """
        data_list = []

        job_id = job_id
        # self.logger.info("get job_id :%s" % (job_id))
        # job_id_pattern = re.compile('\w+-\w+-\w+-\w+-{0}-\w+'.format(job_id))
        # xuwenkai - job - infer/train/dataset - 0afc - 20180130 - 085956 - e1c6 - 6cfkf
        job_id_pattern = re.compile('[\S]*')
        base_pod_pattern = re.compile('[\S]*-[0-9]{8}-[0-9]{6}-[0-9a-z]{4}')
        # task-0afc
        # task_id_pattern = re.compile('(train|infer|dataset)-\w+')


        status_pattern = re.compile(r'[A-Z]+\w+')
        # ip_pattern = re.compile(r'\d+.\d+.\d+.\d+')
        ip_pattern = re.compile(r'\d+[.]\d+[.]\d+[.]\d+')
        node_pattern = re.compile(r'node\d+')
        field_list = ["NAME", "READY", "STATUS", "RESTARTS", "AGE", "IP", "NODE"]
        # self.logger.info("get job_id_pattern :%s" % (job_id_pattern))

        if res:
            pod_list = res.split("\n")
        else:
            get_command = self.get_all_pods_status()
            res = self.exe_command(command=get_command)
            pod_list = res.split("\n")

        tmp_list = []
        for li in pod_list:
            if re.search(str(job_id), li):
                tmp_list.append(li)

        # self.logger.info("get resource list ,tmp_list:%s"%(tmp_list))
        for li in tmp_list:
            # self.logger.info("tmp_list li: %s"%(li))

            # self.logger.info("--------------------------------------------------------------------------------------")
            full_pod_name = re.search(job_id_pattern, li)
            if full_pod_name:
                full_pod_name = full_pod_name.group()
                # self.logger.info("full_pod_name: %s." % (full_pod_name))
            else:
                continue

            base_pod_name = re.search(base_pod_pattern, full_pod_name)
            if base_pod_name:
                base_pod_name = base_pod_name.group()
                # self.logger.info("base_pod_name: %s." % (base_pod_name))
            else:
                continue

            # task_id = re.search(task_id_pattern, full_pod_name)
            # if task_id:
            #     task_id = task_id.group()
            #     # self.logger.info("task_id: %s." % (task_id))
            # else:
            #     task_id = "none"


            # pending/containercreating状态，ip和node为none,要做异常处理
            ip = re.search(ip_pattern, li)
            if ip:
                ip = ip.group()
                # self.logger.info("ip: %s." % (ip))
            else:
                ip = "none"
                # self.logger.info("IP is none")

            node = re.search(node_pattern, li)
            if node:
                node = node.group()
                # self.logger.info("node: %s." % (node))
            else:
                node = "none"
                # self.logger.info("Node is none.")

            status = re.search(status_pattern, li).group()
            # self.logger.info("status: %s." % (status))
            # self.logger.info("--------------------------------------------------------------------------------------")


            data_dict = {}
            data_dict[field_list[0]] = full_pod_name
            data_dict[field_list[2]] = status
            data_dict[field_list[5]] = ip
            data_dict[field_list[6]] = node
            data_dict["base_pod_name"] = base_pod_name
            # data_dict["task_id"] = task_id

            data_list.append(data_dict)

        self.logger.info("The pod info from resource list(multi task): %s" % (data_list))
        return data_list

    def get_pod_list_completed(self, res=None):
        """
        xxx
        """
        data_list = []
        # xuwenkai - job - infer/train/dataset - 0afc - 20180130 - 085956 - e1c6 - 6cfkf
        base_pod_name_pattern = re.compile('[\S]*-[0-9]{8}-[0-9]{6}-[0-9a-z]{4}')
        status_pattern = re.compile(r'Completed')
        # ip_pattern = re.compile(r'\d+.\d+.\d+.\d+')
        ip_pattern = re.compile(r'\d+[.]\d+[.]\d+[.]\d+')
        node_pattern = re.compile(r'node\d+')
        field_list = ["NAME", "READY", "STATUS", "RESTARTS", "AGE", "IP", "NODE"]
        # self.logger.info("get job_id_pattern :%s" % (job_id_pattern))

        if res:
            pod_list = res.split("\n")
        else:
            get_command = self.get_all_pods_status()
            res = self.exe_command(command=get_command)
            pod_list = res.split("\n")

        for li in pod_list:
            self.logger.info("pod_list li: %s" % (li))
            status = re.search(status_pattern, li)
            if status:
                status = status.group()
                self.logger.info("status: %s" % (status))
            else:
                continue

            if status == "Completed":
                # self.logger.info("status: %s." % (status))
                base_pod_name = re.search(base_pod_name_pattern, li)
                if base_pod_name:
                    base_pod_name = base_pod_name.group()
                # self.logger.info("base_pod_name: %s." % (base_pod_name))
                else:
                    continue

                # pending/containercreating状态，ip和node为none,要做异常处理
                ip = re.search(ip_pattern, li)
                if ip:
                    ip = ip.group()
                    # self.logger.info("ip: %s." % (ip))
                else:
                    ip = "none"
                    # self.logger.info("IP is none")

                node = re.search(node_pattern, li)
                if node:
                    node = node.group()
                    # self.logger.info("node: %s." % (node))
                else:
                    node = "none"
                    # self.logger.info("Node is none.")

                data_dict = {}
                data_dict[field_list[2]] = status
                data_dict[field_list[5]] = ip
                data_dict[field_list[6]] = node
                data_dict["base_pod_name"] = base_pod_name

                data_list.append(data_dict)
            else:
                continue

        self.logger.info("The pod info from resource list(final completed check!): %s" % (data_list))
        return data_list

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
        self.logger.info("The pod_base_name is:%s"%(pod_base_name,))

        # get full_pod_name by base_pod_name
        pattern = re.compile(r'{0}-\w+'.format(pod_base_name))
        self.logger.info("The pattern is:%s" % (pattern))
        if res:
            re_res = re.search(pattern, res)
            self.logger.info("The [base_pod_name:full_pod_name] Bool:%s"%(re_res,))
            if re_res:
                full_pod_name = re_res.group()
                self.logger.info("The full_pod_name is:%s"%(full_pod_name,))
                return full_pod_name
            else:
                return None
        pass

    def get_deployment(self):
        # 查看已有部署的容器kubectl get deployment
        return "kubectl get deployment"
        pass

    def desc_by_pod_name(self, full_pod_name=None):
        """
        根据用户传入的pod_name来获取详细的信息
        :param pod_name: 用户传入的pod_name（完整的pod_name）
        :return: 返回describe命令
        """
        # 查看指定pod的详细描述
        # if pod_name != self.pod_name:
        #     return "kubectl describe pod {}".format(pod_name)
        #
        # # 如果用户传入的是用户定义的pod_name则先获取完整的pod_name
        # full_pod_name = self.get_full_pod_name(pod_name)
        if full_pod_name:
            return "kubectl describe pod {}".format(full_pod_name)
        self.logger.info("Don't get the describe because no full_pod_name.")
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
        self.logger.info("No pod_name.")
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
            return read_process_stdout(p)
            # logger.warning("End and the command is: %s" % kwargs['command'])
            # this_output = p.stdout.read()
            # logger.warning("The command is: %s"% (kwargs['command']))
            # logger.warning("The result is: %s"% (this_output))
            # return this_output
        raise ValueError("Not get command to exe.")
        pass


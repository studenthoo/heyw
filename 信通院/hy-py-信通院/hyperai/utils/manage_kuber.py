import os
import sys
import re
import gevent
import subprocess

from hyperai.config import config_value
from hyperai.utils import read_process_stdout


class ManagePod(object):
    """"""

    def __init__(self, job_id, logger, job_dir, task_obj, **kwargs):
        self.job_id = job_id
        self.pod_name = None
        self.yaml_path = None
        self.logger = logger
        self.task_obj = task_obj
        self.job_dir = job_dir
        self.get_com = "kubectl get po -o wide"
        pass

    def generate_yaml(self, command, args, selector_node, cpu_count, memory_count, gpu_count, **kwargs):
        # print "CaffePri   generate_yaml"

        matchExpressions_values = '[%s]' % self.task_obj.node_label
        creater = config_value("creater")
        image = config_value("image_list")["generic_image"]
        base_path = config_value('generic_base_yaml')
        new_dir = config_value('generate_yaml_dir')
        # new_yaml = os.path.join(new_dir, "{}.yaml".format(self.job_id))
        new_yaml = os.path.join(self.job_dir, "{}.yaml".format(self.job_id))

        name = "{}-{}".format(creater, self.job_id)
        metadata_name = selector_name = labels_name = container_name = name

        kind = "Job"
        replicas = 1
        command = str(command)
        args = str(args)
        selector_node = selector_node

        gpu = str(gpu_count)
        cpu = str(cpu_count)
        memory = str(memory_count)
        if not memory.endswith("Gi"):
            memory = "{}Gi".format(memory)
        pythonpath = ":/usr/local/python:" + self.job_dir
        # nfsdir = "/home/nfsdir"
        # hyperai_jobs_dir = "/home/nfsdir"
        nfs_path = config_value("nfs_path")
        hyperai_root = config_value('hyperai_root')

        if base_path:
            with open(base_path, mode='r+') as r_file:
                with open(new_yaml, 'w+') as w_file:
                    for line in r_file.readlines():
                        if line.find("$kind$") >= 0:
                            new_line = line.replace("$kind$", kind)
                            w_file.write(new_line)
                        elif line.find("$replicas$") >= 0:
                            new_line = line.replace("$replicas$", replicas)
                            w_file.write(new_line)
                        elif line.find("$metadata-name$") >= 0:
                            new_line = line.replace("$metadata-name$", metadata_name)
                            w_file.write(new_line)
                        elif line.find("$selector-name$") >= 0:
                            new_line = line.replace("$selector-name$", selector_name)
                            w_file.write(new_line)
                        elif line.find("$labels-name$") >= 0:
                            new_line = line.replace("$labels-name$", labels_name)
                            w_file.write(new_line)
                        elif line.find("$selector-node$") >= 0:
                            new_line = line.replace("$selector-node$", selector_node)
                            w_file.write(new_line)
                        elif line.find("$container-name$") >= 0:
                            new_line = line.replace("$container-name$", container_name)
                            w_file.write(new_line)
                        elif line.find("$image$") >= 0:
                            new_line = line.replace("$image$", image)
                            w_file.write(new_line)
                        elif line.find("$command$") >= 0:
                            new_line = line.replace("$command$", command)
                            w_file.write(new_line)
                        elif line.find("$args$") >= 0:
                            new_line = line.replace("$args$", args)
                            w_file.write(new_line)
                        elif line.find("$gpu$") >= 0:
                            new_line = line.replace("$gpu$", gpu)
                            w_file.write(new_line)
                        elif line.find("$cpu$") >= 0:
                            new_line = line.replace("$cpu$", cpu)
                            w_file.write(new_line)
                        elif line.find("$memory$") >= 0:
                            new_line = line.replace("$memory$", memory)
                            w_file.write(new_line)
                        elif line.find("$mountpath$") >= 0:
                            new_line = line.replace("$mountpath$", nfs_path)
                            w_file.write(new_line)
                        elif line.find("$hyperai_jobs_dir$") >= 0:
                            new_line = line.replace("$hyperai_jobs_dir$", nfs_path)
                            w_file.write(new_line)
                        elif line.find("$hyperai_root$") >= 0:
                            new_line = line.replace("$hyperai_root$", hyperai_root)
                            w_file.write(new_line)
                        elif line.find("$nfsip$") >= 0:
                            new_line = line.replace("$nfsip$", config_value('nfs_ip'))
                            w_file.write(new_line)
                        elif line.find("$nfspath$") >= 0:
                            new_line = line.replace("$nfspath$", config_value('nfs_path'))
                            w_file.write(new_line)
                        elif line.find("$pythonpath$") >= 0:
                            new_line = line.replace("$pythonpath$", pythonpath)
                            w_file.write(new_line)
                        elif line.find("$matchExpressions-values$") >= 0:
                            new_line = line.replace("$matchExpressions-values$", matchExpressions_values)
                            w_file.write(new_line)
                        else:
                            w_file.write(line)
            self.yaml_path = new_yaml
            return new_yaml
        else:
            return None

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

    def create_pod(self, new_path=None):
        if not new_path:
            new_path = self.yaml_path
        job_id = self.job_id
        create_com = "kubectl apply -f {}".format(new_path)
        msg = self.short_exec_com(create_com)
        # print "* * Create Pod: %s" % msg
        self.logger.info("* Create Pod: %s" % msg)
        # num = 0
        while not self.pod_name:
            gevent.sleep(1)
            get_res = self.short_exec_com()
            pod_name_list = self.parse_pod_name(job_id, get_res)
            if len(pod_name_list) > 0:
                self.pod_name = pod_name_list[0]
        pod_sign = False
        while not pod_sign:
            gevent.sleep(1)
            get_res = self.short_exec_com()
            pod_msg = self.parse_pod_msg(self.pod_name, get_res)
            if pod_msg and pod_msg[2] == "Running":
                self.logger.info("Pod Status:  [%s]" % pod_msg[2])
                self.task_obj.pre_allocate_res_task()
                self.logger.info("- " * 60)
                return True
            elif pod_msg and pod_msg[2] in ["Pending", "ContainerCreating"]:
                self.logger.info("Pod Status:  [%s]" % pod_msg[2])
                if self.task_obj.aborted.is_set():
                    # self.delete_pod()
                    msg = 'Abort Pod Successed: [{}].'.format(pod_msg[2])
                    self.logger.info(msg)
                    return False
                # gevent.sleep(1)
            else:
                raise RuntimeError("Pod Status Error: [%s]-[%s]" % (pod_msg[0], pod_msg[2]))

    def delete_pod(self, job_id=None):
        if hasattr(self, 'yaml_path'):
            del_cmd = "kubectl delete -f {}".format(self.yaml_path)
            msg = self.short_exec_com(command=del_cmd)
            self.logger.info("Delete pod by yaml: %s " % msg)
            return True
        elif hasattr(self, 'pod_name'):
            del_cmd = "kubectl delete job {}".format(self.pod_name)
            msg = self.short_exec_com(command=del_cmd)
            # print "* * Delete pod by pod_name: %s " % msg
            return True
        elif job_id:
            get_res = self.short_exec_com()
            pod_name_list = self.parse_pod_name(job_id, get_res)
            if len(pod_name_list) > 0:
                pod_name = pod_name_list[0]
                del_cmd = "kubectl delete job {}".format(pod_name)
                msg = self.short_exec_com(command=del_cmd)
                # print "* * Delete pod by pod_name: %s " % msg
                return True
        else:
            self.logger.erro("Not Found Pod Name.")
            return False

    def short_exec_com(self, command="kubectl get po -a -o wide"):
        p = subprocess.Popen(args=command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        return read_process_stdout(p)

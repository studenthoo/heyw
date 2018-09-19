import os
import sys
import re
import gevent
import subprocess

from hyperai.config import config_value
from hyperai.utils import read_process_stdout


class CaffePri(object):
    """"""
    def __init__(self, job_id, **kwargs):
        self.job_id = job_id
        self.pod_name = None
        self.yaml_path = None
        self.get_com = "kubectl get po -a -o wide"
        pass

    def generate_yaml(self, command, args, selector_node, cpu_count, memory_count, gpu_count, **kwargs):
        print "CaffePri   generate_yaml"

        creater = config_value("creater")
        image = config_value("image_list")["generic_image"]
        base_path = config_value('generic_base_yaml')
        new_dir = config_value('generate_yaml_dir')
        new_yaml = os.path.join(new_dir, "{}.yaml".format(self.job_id))

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

        nfsdir = "/home/nfsdir"
        hyperai_jobs_dir = "/home/nfsdir"

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
                            new_line = line.replace("$mountpath$", nfsdir)
                            w_file.write(new_line)
                        elif line.find("$hyperai_jobs_dir$") >= 0:
                            new_line = line.replace("$hyperai_jobs_dir$", hyperai_jobs_dir)
                            w_file.write(new_line)
                        elif line.find("$nfspath$") >= 0:
                            new_line = line.replace("$nfspath$", nfsdir)
                            w_file.write(new_line)
                        elif line.find("$nfsip$") >= 0:
                            new_line = line.replace("$nfsip$", config_value('nfs_ip'))
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
        print "* * Create Pod: %s" % msg
        num = 0
        while not self.pod_name:
            get_res = self.short_exec_com()
            pod_name_list = self.parse_pod_name(job_id, get_res)
            if len(pod_name_list) > 0:
                self.pod_name = pod_name_list[0]
            elif num < 10:
                num += 1
            else:
                raise RuntimeError("")

        print "loop 1 Down"
        pod_sign = False
        time_out = 0
        while not pod_sign:
            get_res = self.short_exec_com()
            pod_msg = self.parse_pod_msg(self.pod_name, get_res)
            if pod_msg and pod_msg[2] == "Running":
                pod_sign = True
                print "Loop 2 Down ."
                return True
            elif pod_msg and pod_msg[2] in ["Pending", "ContainerCreating"]:
                gevent.sleep(1.5)
                pass
                time_out += 1
                pass
            else:
                # self.delete_pod()
                raise RuntimeError("Pod Status Error: [%s]-[%s]" % (pod_msg[0], pod_msg[2]))

    # @staticmethod
    def delete_pod(self):
        delete_command = "kubectl delete -f {}".format(self.yaml_path)
        msg = self.short_exec_com(command=delete_command)
        print "* * Delete pod : %s " % msg

    def short_exec_com(self, command="kubectl get po -a -o wide"):
        p = subprocess.Popen(args=command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        return read_process_stdout(p)
        # return p.stdout.read()


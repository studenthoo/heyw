# !/usr/bin/python
# -*- encoding: utf-8 -*-

import os
import shutil
import logging
import subprocess
import argparse
import platform
import datetime
import time
import re
import sys
import signal
import gevent.event
# from log_config import K8sLog
from hyperai import utils
from hyperai.tools.kuber import config_dir
from hyperai.config import config_value
import hyperai.tools.kuber.kube_log as kubelog

from kube import ManageKubernets
from yaml import ManageYamlFile
from hyperai.utils import read_process_stdout


# constant
base_dir = os.path.dirname(os.path.abspath(__file__))


def init_kubelog_logger(flag,job_id):
    logger = kubelog.setup_logging(flag,job_id)
    # logger = kubelog.JobIdLoggerAdapter(logging.getLogger('kube'),{'job_id': job_id},)
    return logger


def generate_kube_yaml(base_yaml_file_path=None,
                       generated_yaml_file_path=None,
                       arguments=None,
                       selector_node=None,
                       selector_name=None,
                       labels_name=None,
                       metadata_name=None,
                       container_name=None,
                       kind=None,
                       image=None,
                       command=None,
                       gpu=None,
                       cpu=None,
                       memory=None,
                       nfsdir=None,
                       hyperai_jobs_dir=None,
                       replicas=str(1),
                       **kwargs):
    base_yaml_file_path = base_yaml_file_path
    generated_yaml_file_path = generated_yaml_file_path
    kind = kind
    metadata_name = metadata_name
    replicas = replicas
    selector_name = selector_name
    selector_node = selector_node
    container_name = container_name
    labels_name = labels_name
    image = image
    command = str(command)
    args = str(arguments)
    gpu = str(gpu)
    cpu = '"' + str(cpu) + '"'
    memory = str(memory)
    nfsdir = str(nfsdir)
    hyperai_jobs_dir = str(hyperai_jobs_dir)
    # args = '["/usr/bin/python2"]'
    # command = '["sh","-c"]'
    # args = '["/usr/sbin/sshd -D"]'

    if base_yaml_file_path:
        with open(base_yaml_file_path, mode='r+') as r_file:
            with open(generated_yaml_file_path, 'w+') as w_file:
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
                    else:
                        w_file.write(line)
        return generated_yaml_file_path
    else:
        logger.error("Not found the file.")
        return None


def exe_command(command=None):
    """
    execute the action(create dateset,train,inf) ,simple sentences,not main logs output
    :param command:
    :return: exe result
    """

    if command:
        p = subprocess.Popen(args=command,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             close_fds=False if platform.system() == 'Windows' else True,
                             cwd=base_dir,
                             shell=True)
        return read_process_stdout(p)
        # this_output = p.stdout.read()
        # logger.info("The command is: %s"%(command))
        # logger.info("The result is: %s"%(this_output))
        # return this_output
    else:
        logger.error("The command not get!")
        raise Exception("The command not get!")


def create_kube_job(kube_obj):
    create_kube_job_start = time.time()
    create_command = kube_obj.create_pods()
    logger.info("Return the create kube job command: %s" % create_command)
    ret_create_result = exe_command(command=create_command)
    logger.info("Return the create kube job result: %s" % ret_create_result)

    create_kube_job_end = time.time()
    create_kube_job_duration = create_kube_job_end - create_kube_job_start
    return ret_create_result


def get_res_list(kube_obj, kube_pod_type):
    logger.info("Waitting ten seconds.")
    time.sleep(10)
    if kube_pod_type:
        get_res_command = kube_obj.get_all_pods_status()
    else:
        get_res_command = kube_obj.get_all_pods()

    logger.info("Return the query kube job command: %s" % (get_res_command,))
    get_res_list = exe_command(command=get_res_command)
    logger.info("Return the query kube job resource list:\n %s" % (get_res_list,))
    return get_res_list


def delete_kube_job(kube_obj, generated_yaml_file_path):
    del_yaml_command = kube_obj.delete_by_yaml(generated_yaml_file_path)
    logger.info("Return the delete kube job command: %s" % (del_yaml_command,))
    get_del_status = exe_command(command=del_yaml_command)
    logger.info("Return the delete kube job result: %s" % (get_del_status,))
    # 'job "xuwenkai-job-20180119-163437-7db0" deleted\n'

    if get_del_status.find("deleted"):
        logger.info("Delete kube job completed normally!")
        return True
    else:
        logger.error("Delete kube job failed!")
        return False


def delete_kube_job_batch(kube_obj, file_path):
    delete_count = 0
    for value in file_path:
        if os.path.exists(value):
            del_yaml_command = kube_obj.delete_by_yaml(value)
            # logger.info("---------------dataset del_yaml_command:%s" % (del_yaml_command,))
            get_del_status = exe_command(command=del_yaml_command)
            # logger.info("----------------dataset get_del_status:%s" % (get_del_status,))
            if get_del_status.find("deleted"):
                delete_count += 1
        else:
            return True
    if delete_count:
        logger.info("Delete kube jobs completed normally in batches! delete_count: %s"%(delete_count))
        return True
    else:
        logger.info("Delete kube jobs failed in batches! file_path: %s" % (file_path))
        return False


def get_job_info(kube_obj, base_pod_name):
    # ret_research_command = "kubectl get pod -a -o wide"
    ret_research_command = kube_obj.get_all_pods_status()
    logger.info("Return the query kube job command: %s" % ret_research_command)
    ret_res_list = exe_command(command=ret_research_command)
    # logger.info("Return the query kube job resource list: %s" % ret_res_list)
    ret_job_dict = kube_obj.get_msg_pod_field(base_pod_name=base_pod_name, res=ret_res_list)
    logger.info("Return the query kube job info dict: %s" % ret_job_dict)

    if ret_job_dict:
        return ret_job_dict
    else:
        return None


def get_status_list(kube_obj, job_id):
    # ret_research_command = "kubectl get pod -a -o wide"
    ret_research_command = kube_obj.get_all_pods_status()
    logger.info("Return the query kube job command: %s" % ret_research_command)
    ret_res_list = exe_command(command=ret_research_command)
    # logger.info("Return the query kube job resource list: %s" % ret_res_list)
    ret_dict_list = kube_obj.get_msg_pod_field_list(job_id=job_id, res=ret_res_list)
    logger.info("Return the query kube job info list(dataset): %s" % ret_dict_list)

    return ret_dict_list


def judge_yaml_id_repeat(kube_pod_type, base_pod_name):
    # checking for the existence of yaml_id
    exist = None
    while True:
        if kube_pod_type:
            get_res_command = ManageKubernets.get_all_pods_status()
        else:
            get_res_command = ManageKubernets.get_all_pods()

        get_res_list = exe_command(command=get_res_command)
        pattern = re.compile(base_pod_name)
        if re.search(pattern, get_res_list):
            exist = True
            logger.error("The pod has existed: %s"%base_pod_name)
        else:
            logger.warning("The yaml_id can be created: %s" % (base_pod_name))
            exist = False
            break

    if exist:
        return True
    else:
        return False


def get_yaml_path(yaml_id):
    base_yaml_file_path = config_value('generic_base_yaml')
    base_yaml_file_name = os.path.splitext(base_yaml_file_path)[-1]
    # base_yaml_file_name = "base_job_new.yaml"
    logger.info("The base yaml file name is: %s" % base_yaml_file_name)
    new_yaml_file_name = "%s.yaml" % (yaml_id,)
    logger.info("The generated yaml file name is: %s" % new_yaml_file_name)

    generate_yaml_dir = config_value('generate_yaml_dir')   # .../generate_yamls

    logger.info("The base yaml file path: %s" % (base_yaml_file_path,))



    generated_yaml_file_path = os.path.join(generate_yaml_dir, new_yaml_file_name)
    logger.info("The generated yaml file path: %s" % (generated_yaml_file_path,))

    return base_yaml_file_path, generated_yaml_file_path


def delete_yaml(generated_yaml_file_path):
    if os.path.exists(generated_yaml_file_path):
        delete_yaml_status = os.remove(generated_yaml_file_path)
        logger.info("Delete kube job yaml file completed normally! the status is: %s" % (delete_yaml_status))
    else:
        logger.error("File is not exist! generated_yaml_file_path: %s"%(generated_yaml_file_path))


def delete_yaml_batch(file_path):
    delete_yaml_count = 0
    for value in file_path:
        if os.path.exists(value):
            delete_yaml_status = os.remove(value)
            delete_yaml_count += 1
        else:
            logger.error("file path not exist! value: %s" % (value))


    if delete_yaml_count:
        logger.info("Delete kube jobs yaml file completed normally in batches!: %s" % (delete_yaml_status))
        return True
    else:
        logger.error("Delete kube jobs yaml file failed in batches! file_path: %s" % (file_path))
        return False


def transfer_output(get_logs_command):
    if get_logs_command:
        p = subprocess.Popen(args=get_logs_command,
                             bufsize=-1,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             close_fds=False if platform.system() == 'Windows' else True,
                             cwd=base_dir,
                             shell=True)

        try:
            while p.poll() is None:
                for line in utils.nonblocking_readlines(p.stdout):
                    if line:
                        print(line)
                        sys.stdout.flush()

        except Exception as e:
            logger.error(e)
            p.terminate()
            raise
    else:
        logger.error("The logs -f command is not exist!.")

def abort_kube_job(signum, frame):

    logger.info("signal.SIGTERM come in and abort delete kube job start!")
    flag = args['flag'][0]
    job_id = args['job_id'][0]

    logger.info("Abort flag: %s" % (flag))
    logger.info("Abort job_id: %s" % (job_id))
    yaml_dir = config_dir('yaml_dir')
    new_yaml_dir = os.path.join(yaml_dir, 'generate_yamls')
    kube_obj = ManageKubernets(generated_yaml_file_path=new_yaml_dir, logger=logger)

    abort_pod_query_times = 0
    while True:
        all_pod_info_command = kube_obj.get_all_pods_status()
        all_pod_info_result = exe_command(all_pod_info_command)
        logger.info("all_pod_info_result: %s" % (all_pod_info_result))
        abort_job_list = kube_obj.get_msg_pod_field_list(job_id=job_id, res=all_pod_info_result)

        if abort_job_list:
            logger.info("abort_job_list: %s" % (abort_job_list))
            abort_yamls_list = []
            for value in abort_job_list:
                value_path = new_yaml_dir + "/" + value.get("base_pod_name") + ".yaml"
                # /home/nfsdir/public/yaml_dir/generate_yamls/hy-job-ds-create-db -b6da-20180208-110612-5a5c.yaml
                logger.info("Abort value_path: %s" % (value_path))
                abort_yamls_list.append(value_path)

            logger.info("abort_yamls_list: %s" % (abort_yamls_list))
            ret_del_status = delete_kube_job_batch(kube_obj, abort_yamls_list)
            if ret_del_status:
                delete_yaml_batch(abort_yamls_list)
            break

        else:
            abort_pod_query_times += 1
            if abort_pod_query_times < 4:
                continue
            else:
                raise Exception("Abort delete kube job timesout! ")

    logger.info("signal.SIGTERM in and abort delete kube job end!")

resource_status_list = {}
resource_status_cur = {"job_id": None, "status": None, "full_pod_name": None, "use_kube_res_status": None,
                       "nouse_kube_res_status": None}

def main_method(*args, **kwargs):
    """
    :param args:
    :param kwargs:
    :return:
    """
    # get the arguments passed from task.run args(create dataset,train,inf)


    flag = kwargs['flag'][0]
    task_id = kwargs['task_id'][0]
    job_id = kwargs['job_id'][0]

    gpu_count = kwargs['gpu_count'][0]
    cpu_count = kwargs['cpu_count'][0]
    memory_count = kwargs['memory_count'][0]
    nfsdir = kwargs['nfsdir'][0]
    hyperai_jobs_dir = nfsdir

    logger.info("---------------------------------")
    logger.info("Main method the gpu_count is: %s" % gpu_count)
    logger.info("Main method the cpu_count is: %s" % cpu_count)
    logger.info("Main method the memory_count is: %s" % memory_count)
    logger.info("Main method the nfsdir is: %s" % nfsdir)
    logger.info("Main method the hyperai_jobs_dir is: %s" % hyperai_jobs_dir)
    logger.info("---------------------------------")


    cmd = kwargs['command']
    args = kwargs['argument']

    logger.info("Main method the flag is: %s" % flag)
    logger.info("Main method the task_id is: %s" % task_id)
    logger.info("Main method the job_id is: %s" % job_id)

    logger.info("Main method the cmd is: %s" % cmd)
    logger.info("Main method the args is: %s" % args)

    if gpu_count == "None":
        if flag == "dataset" and "infer":
            gpu_count = 0
        else:
            gpu_count = 1

    if cpu_count == "None":
        cpu_count = 4

    logger.info("memory_count type: %s"%(type(memory_count)))

    if memory_count.endswith("Gi"):
        memory_count = memory_count
    else:
        memory_count = "16Gi"

    logger.info("---------------------------------")
    logger.info("Main method the gpu_count is: %s" % gpu_count)
    logger.info("Main method the cpu_count is: %s" % cpu_count)
    logger.info("Main method the memory_count is: %s" % memory_count)
    logger.info("---------------------------------")

    back_id = flag + "-" + task_id + "-" + job_id

    # init yaml scripts arguments
    # Its convenient for testing by filling in your name,e.g:hyperai
    # creater = "hy"
    creater = config_value('creater')
    selector_node = "node02"
    # kind = ["ReplicationController","Job"]
    kube_pod_type = "Job"
    lower_pod_type = str.lower(kube_pod_type)
    # back_id = '%s-%s' % (time.strftime('%Y%m%d-%H%M%S'), os.urandom(2).encode('hex'))


    base_pod_name = "{0}-{1}-{2}".format(creater, lower_pod_type, back_id)
    # xuwenkai - job - infer/train/dataset - 4a80 - 20180201 - 012022 - 7422 - lz9qd
    # images = ['hyperai:hyperai_cloud_v1.0.0', 'hyperai_py:hyperai20180302','hyperai_py:hyperai20180306','hyperai_py:hyperai20180308']
    # image = images[1]

    image = config_value('image_list')['generic_image']
    print("In Main_kube: images=", image)

    selector_name = base_pod_name
    checkout_selector_name = base_pod_name
    metadata_name = base_pod_name
    labels_name = base_pod_name
    container_name = base_pod_name
    generated_yaml_id = base_pod_name

    logger.info("The vital args: base_pod_name: %s" % (base_pod_name))
    logger.info("The vital args: images: %s" % (image))
    logger.info("The vital args: selector_name: %s" % (selector_name))
    logger.info("The vital args: checkout_selector_name: %s" % (checkout_selector_name))
    logger.info("The vital args: metadata_name: %s" % (metadata_name))
    logger.info("The vital args: labels_name: %s" % (labels_name))
    logger.info("The vital args: container_name: %s" % (container_name))
    logger.info("The vital args: generated_yaml_id: %s" % (generated_yaml_id))

    # judge the existence of yaml id
    bool_type = judge_yaml_id_repeat(kube_pod_type, generated_yaml_id)
    if bool_type:
        logger.info("Yaml id exist")
    else:
        logger.info("Will create new yaml id")

    base_yaml_file_path, generated_yaml_file_path = get_yaml_path(generated_yaml_id)
    logger.info("Get the base yaml file_path is: %s" % base_yaml_file_path)
    logger.info("Get the generated yaml file path is: %s" % generated_yaml_file_path)


    gene_yaml_start = time.time()
    # generate new templates yaml file，generate_kube_yaml
    generated_yaml_file_path = generate_kube_yaml(base_yaml_file_path=base_yaml_file_path,
                                            generated_yaml_file_path=generated_yaml_file_path,
                                            kind=kube_pod_type,
                                            command=cmd,
                                            arguments=args,
                                            image=image,
                                            container_name=container_name,
                                            selector_node=selector_node,
                                            selector_name=selector_name,
                                            labels_name=labels_name,
                                            metadata_name=metadata_name,
                                            gpu=gpu_count,
                                            cpu=cpu_count,
                                            memory=memory_count,
                                            hyperai_jobs_dir=hyperai_jobs_dir,
                                            nfsdir=nfsdir)

    logger.info("Get the generated_yaml_file_path: %s" % generated_yaml_file_path)
    gene_yaml_end = time.time()
    gene_yaml_duration = gene_yaml_end - gene_yaml_start

    resource_status_cur["job_id"] = job_id

    kube_obj = ManageKubernets(generated_yaml_file_path=generated_yaml_file_path, pod_name=base_pod_name, logger=logger)
    logger.info("Create a instance of ManageKubernets: %s" % kube_obj)

    # first check completed and delete job
    all_pod_info_command = kube_obj.get_all_pods_status()
    all_pod_info_result = exe_command(all_pod_info_command)
    logger.info("all_pod_info_result: %s" % (all_pod_info_result))
    completed_jobs_list = kube_obj.get_pod_list_completed(all_pod_info_result)
    logger.info("completed_jobs_list: %s" % (completed_jobs_list))
    completed_yamls_list = []
    for value in completed_jobs_list:
        value_path = os.path.dirname(generated_yaml_file_path) + "/" + value.get("base_pod_name") + ".yaml"
        # /home/nfsdir/public/yaml_dir/generate_yamls/hy-job-ds-create-db -b6da-20180208-110612-5a5c.yaml
        logger.info("value_path: %s" % (value_path))
        completed_yamls_list.append(value_path)

    logger.info("completed_yamls_list: %s" % (completed_yamls_list))
    ret_del_status = delete_kube_job_batch(kube_obj, completed_yamls_list)
    if ret_del_status:
        delete_yaml_batch(completed_yamls_list)

    ret_create_result = create_kube_job(kube_obj)
    ret_query_command = kube_obj.get_all_pods_status()
    logger.info("Return the query kube job command: %s" % ret_query_command)

    get_full_pod_name_start = time.time()
    is_created_count = 0
    while True:
        ret_res_list = exe_command(command=ret_query_command)
        full_pod_name = kube_obj.get_full_pod_name(ret_res_list, base_pod_name)
        logger.info("The kubernetes created job by file! full_pod_name: %s" % (full_pod_name))

        if ret_create_result.find("created") or full_pod_name is not None:
            logger.info("Kube create job succeed! INFO: %s,\n,full_pod_name: %s" % (ret_create_result, full_pod_name))
            break
        else:
            time.sleep(2)
            is_created_count += 1
            if is_created_count < 10:
                continue
            else:
                logger.error("Kube create job time out %s seconds!" % (is_created_count))
                logger.error("Kube create job failed! ERROR: %s,full_pod_name: %s" % (ret_create_result, full_pod_name))
                exit(-1)

    get_full_pod_name_end = time.time()
    get_full_pod_name_duration = get_full_pod_name_end - get_full_pod_name_start

    is_ret_job_info_count = 0
    polling_time = 2
    polling_times = 0
    pending_time = 2
    pending_times = 0
    # global polling_flag
    polling_flag = True
    creating_times = 0
    dataset_creating_times = 0
    is_ret_job_info_count = 0

    try:
        while polling_flag:
            ret_job_dict = get_job_info(kube_obj, base_pod_name)
            if ret_job_dict:
                ret_status = ret_job_dict.get("STATUS")
                full_pod_name = ret_job_dict.get("NAME")
                logger.info("While polling flag: %s" % (flag))
                logger.info("While polling current kube job status: %s" % (ret_status))
                logger.info("While polling full_pod_name: %s" % (full_pod_name))
            else:
                is_ret_job_info_count += 1
                if is_ret_job_info_count < 10:
                    time.sleep(1)
                    continue
                else:
                    logger.error("Not get the return job info! create container failed!")
                    exit(-1)
            if ret_status == "Running":
                logger.info("Enter status: %s" % (ret_status))
                logger.info("Task_id: %s" % (task_id))
                logger.info("Use_kube_resource_status: %s" % ("True"))
                logger.info("Nouse_kube_resource_status: %s" % ("False"))

                kube_job_running_start = time.time()
                logger.info("Kube running job by file successed! full_pod_name: %s" % (full_pod_name))
                resource_status_cur['full_pod_name'] = full_pod_name

                get_logs_command = kube_obj.get_log_by_pod_name(full_pod_name)
                logger.info("Return the get_pod_name command is: %s" % get_logs_command)
                transfer_output(get_logs_command)

                kube_job_running_duration = time.time() - kube_job_running_start
                logger.info("%s during_time: %s" % (ret_status,kube_job_running_duration))
                continue
            elif ret_status == "ContainerCreating" or ret_status == "CreateContainerConfigError":
                logger.info("Enter status: %s" % (ret_status))
                time.sleep(1)
                creating_times+=1
                if creating_times <10:
                    logger.info("creating_times: %s"%(creating_times))
                    continue
                else:
                    logger.error("creating_times: %s" % (creating_times))
                    logger.error("%s Timesout!" % (ret_status))
                    raise Exception("%s Timesout!"%(ret_status))
            elif ret_status == "Pending" or ret_status == "Error":
                logger.info("Enter status: %s" % (ret_status))

                describe_cmd = kube_obj.desc_by_pod_name(full_pod_name)
                describe_result = exe_command(describe_cmd)
                logger.info("describe_result: %s"%(describe_result))

                get_logs_command = kube_obj.get_log_by_pod_name(full_pod_name)
                logger.info("Return the logs command is: %s" % get_logs_command)
                logs_result = exe_command(get_logs_command)
                logger.info("Return the logs result is: %s" % logs_result)

                pengding_error_kube_job_start = time.time()
                time.sleep(polling_time)
                polling_times += 1
                if polling_times < 10:
                    continue
                else:
                    logger.error("Kube pending/error job time out %s seconds!" % (polling_times * polling_time))
                    ret_del_status = delete_kube_job(kube_obj, generated_yaml_file_path)
                    if ret_del_status:
                        logger.error("Kube delete job succeed! full_pod_name: %s" % (full_pod_name))
                        # delete_yaml(generated_yaml_file_path)
                        logger.info("Use_kube_resource_status: %s" % ("False"))
                        logger.info("Nouse_kube_resource_status: %s" % ("True"))

                        pengding_error_kube_job_dur = time.time() - pengding_error_kube_job_start
                        logger.info("%s during_time: %s" % (ret_status,pengding_error_kube_job_dur))
                        logger.error("%s Timesout!"%(ret_status))
                        raise Exception("%s Timesout!"%(ret_status))
                        exit(-1)
                    else:
                        logger.error("Kube delete job failed! full_pod_name: %s" % (full_pod_name))
                        logger.error(
                            "Kube delete job by file path manually,Administrator! generated_yaml_file_path: %s" % (generated_yaml_file_path))
                        logger.error("%s Timesout!" % (ret_status))
                        raise Exception("%s Timesout!" % (ret_status))
                        exit(-1)
            elif ret_status == "CrashLoopBackOff" or ret_status == "RunContainerError":
                logger.info("Enter status: %s" % (ret_status))

                describe_cmd = kube_obj.desc_by_pod_name(full_pod_name)
                describe_result = exe_command(describe_cmd)
                logger.info("describe_result: %s" % (describe_result))

                get_logs_command = kube_obj.get_log_by_pod_name(full_pod_name)
                logger.info("Return the logs command is: %s" % get_logs_command)
                logs_result = exe_command(get_logs_command)
                logger.info("Return the logs result is: %s" % logs_result)

                crash_kube_job_start = time.time()
                ret_del_status = delete_kube_job(kube_obj, generated_yaml_file_path)
                if ret_del_status:
                    logger.error("Kube delete job succeed! full_pod_name: %s" % (full_pod_name))
                    # delete_yaml(generated_yaml_file_path)
                    logger.info("Use_kube_resource_status: %s" % ("False"))
                    logger.info("Nouse_kube_resource_status: %s" % ("True"))

                    crash_kube_job_dur = time.time() - crash_kube_job_start
                    logger.info("%s during_time: %s" % (ret_status,crash_kube_job_dur))
                    raise Exception("container:%s"%(ret_status))
                else:
                    logger.error("Kube delete job failed! full_pod_name: %s" % (full_pod_name))
                    logger.error("Kube delete job by file path manually,Administrator! generated_yaml_file_path: %s" % (generated_yaml_file_path))
                    raise Exception("container:%s" % (ret_status))
            elif ret_status == "Completed":
                logger.info("Enter status: %s" % (ret_status))

                logger.info("Kube completed job by file successed! full_pod_name: %s" % (full_pod_name))

                delete_kube_job_start = time.time()
                ret_del_status = delete_kube_job(kube_obj, generated_yaml_file_path)
                delete_kube_job_duration = time.time() - delete_kube_job_start
                logger.info("%s during_time: %s" % (ret_status,delete_kube_job_duration))

                if ret_del_status:
                    logger.info("Kube delete job by file successed! full_pod_name: %s" % (full_pod_name))
                    delete_yaml(generated_yaml_file_path)
                    logger.info("Use_kube_resource_status: %s" % ("False"))
                    logger.info("Nouse_kube_resource_status: %s" % ("True"))
                    break
                else:
                    logger.error("Kube delete job by file failed! full_pod_name: %s" % (full_pod_name))
                    logger.error("Kube delete job by file path manually,Administrator! generated_yaml_file_path: %s" % (generated_yaml_file_path))
                    exit(0)
            elif ret_status == "Terminating":
                logger.info("Enter status: %s" % (ret_status))
                continue
            else:
                logger.info("Else delete job! full_pod_name: %s" % (full_pod_name))
                ret_del_status = delete_kube_job(kube_obj, generated_yaml_file_path)
                if ret_del_status:
                    logger.info("Kube delete job by file successed! full_pod_name: %s" % (full_pod_name))
                    # delete_yaml(generated_yaml_file_path)
                    logger.info("Use_kube_resource_status: %s" % ("False"))
                    logger.info("Nouse_kube_resource_status: %s" % ("True"))
                    exit(-1)
                else:

                    logger.error("Kube delete job by file failed! full_pod_name: %s" % (full_pod_name))
                    logger.error(
                        "Kube delete job by file path manually,Administrator! generated_yaml_file_path: %s" % (
                            generated_yaml_file_path))
                    exit(-1)
                break
    except KeyboardInterrupt:
        logger.error("KeyboardInterrupt")
        logger.info("KeyboardInterrupt delete job! full_pod_name: %s" % (full_pod_name))
        ret_del_status = delete_kube_job(kube_obj, generated_yaml_file_path)
        if ret_del_status:
            logger.info("Kube delete job by file successed! full_pod_name: %s" % (full_pod_name))
            # delete_yaml(generated_yaml_file_path)
            logger.info("Use_kube_resource_status: %s" % ("False"))
            logger.info("Nouse_kube_resource_status: %s" % ("True"))
        else:
            
            logger.error("Kube delete job by file failed! full_pod_name: %s" % (full_pod_name))
            logger.error("Kube delete job by file path manually,Administrator! generated_yaml_file_path: %s" % (
            generated_yaml_file_path))
        raise Exception("container:%s" % (KeyboardInterrupt))
    except Exception as e:
        logger.error(e)
        raise

    logger.info("The task_id-job_id: [%s]-[%s] end!" % (task_id,job_id))


if __name__ == "__main__":
    """
    pass the arguments
    """
    print "Main Kuber Start ... "
    parse = argparse.ArgumentParser()
    parse.add_argument('-m', '--main_process_start', default=None, help="main_process_start")
    parse.add_argument('-f', '--flag', default=None, help="flag")
    parse.add_argument('-j', '--job_id', default=None, help="job_id")
    parse.add_argument('-t', '--task_id', default=None, help="task_id")
    parse.add_argument('-c', '--command', default=None, help="command")
    parse.add_argument('-a', '--argument', default=None, help="task_argument")

    parse.add_argument('-gpu', '--gpu_count', default=None, help="task_argument")
    parse.add_argument('-cpu', '--cpu_count', default=None, help="task_argument")
    parse.add_argument('-memory', '--memory_count', default=None, help="task_argument")

    parse.add_argument('-n', '--nfsdir', default=None, help="nfsdir")

    args = vars(parse.parse_args())
    args['main_process_start'] = [str(args['main_process_start'])]
    args['flag'] = [str(args['flag'])]
    args['job_id'] = [str(args['job_id'])]
    args['task_id'] = [str(args['task_id'])]
    args['command'] = [str(args['command'])]
    args['argument'] = args['argument']

    args['gpu_count'] = [str(args['gpu_count'])]
    args['cpu_count'] = [str(args['cpu_count'])]
    args['memory_count'] = [str(args['memory_count'])]

    args['nfsdir'] = [str(args['nfsdir'])]

    logger = init_kubelog_logger(args['flag'][0], args['job_id'][0])
    logger.info("The main_process_start is: %s" % args['main_process_start'])
    logger.info("The flag is: %s" % args['flag'])
    logger.info("The job_id is: %s" % args['job_id'])
    logger.info("The task_id is: %s" % args['task_id'])
    logger.info("The command is: %s" % args['command'])
    logger.info("The argument is: %s" % args['argument'])

    logger.info("The gpu_count is: %s" % args['gpu_count'])
    logger.info("The cpu_count is: %s" % args['cpu_count'])
    logger.info("The memory_count is: %s" % args['memory_count'])

    logger.info("The nfsdir is: %s" % args['nfsdir'])

    signal.signal(signal.SIGTERM, abort_kube_job)

    main_process_start = float(args['main_process_start'][0])
    main_method_start = time.time()
    main_method(command=args['command'], argument=args['argument'], job_id=args['job_id'], task_id=args['task_id'],
                flag=args['flag'],gpu_count=args['gpu_count'],cpu_count=args['cpu_count'],memory_count=args['memory_count'],nfsdir=args['nfsdir'])
    main_method_dur = time.time() - main_method_start
    main_process_dur = time.time() - main_process_start






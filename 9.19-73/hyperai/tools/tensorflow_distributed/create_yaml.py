#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-2017, NVIDIA CORPORATION.  All rights reserved.
# from __future__ import absolute_import

import os
import logging
import subprocess
import argparse
import platform
import datetime
import time
import re
import sys
import signal
import json

from kube import ManageKubernets
from threading import Thread
from multiprocessing import Process
from hyperai.utils import read_process_stdout


# constant
base_dir = os.path.dirname(os.path.abspath(__file__))
# logger = K8sLog()

base_path = os.path.join(os.path.dirname(os.path.abspath(os.path.abspath(__file__))), 'log')
k8s_path = os.path.join(base_path, 'distributed.log')

# log config
logger = logging.getLogger("k8s")
logger.setLevel(logging.DEBUG)
# save to the file
fh = logging.FileHandler(k8s_path)
fh.setLevel(logging.DEBUG)
# Output to the terminal
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.WARN)
formatter = logging.Formatter("%(asctime)s %(filename)s %(funcName)s %(lineno)d: [%(levelname)s] %(message)s")
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(ch)
logger.addHandler(fh)
all_ip = []
pod_name_list = []
new_yaml_list = []
num = 0

def get_new_yaml(base_yaml,
                 new_yaml="new_yaml_03.yaml",
                 arguments=None,
                 container_name="base-01",
                 labels_name="base-01",
                 metadata_name="base-01",
                 kind="Job",
                 image="hyperai:hyperai20180206",
                 command='["sh", "-c"]',
                 gpu_count=1,
                 cpu_count=4,
                 memory='8Gi',
                 nfsdir=None,
                 hyperai_jobs_dir=None,
                 **kwargs):
    read_file = base_yaml
    new_yaml = new_yaml
    kind = kind
    metadata_name = metadata_name
    gpu = str(gpu_count)
    cpu = str(cpu_count)
    memory = str(memory)
    container_name = container_name
    labels_name = labels_name
    image = image
    command = command
    nfsdir = str(nfsdir)
    hyperai_jobs_dir = str(hyperai_jobs_dir)

    args = str(arguments)
    if read_file:
        new_yaml = os.path.join(os.path.dirname(os.path.abspath(__file__)), new_yaml)
        new_yaml_list.append(new_yaml)
        with open(read_file, mode='r+') as r_file:
            with open(new_yaml, 'w+') as w_file:
                for line in r_file.readlines():
                    # 找得到返回值是起始下标，找不到返回值是-1
                    if line.find("$kind$") >= 0:
                        new_line = line.replace("$kind$", kind)
                        w_file.write(new_line)
                    elif line.find("$replicas$") >= 0:
                        new_line = line.replace("$replicas$", replicas)
                        w_file.write(new_line)
                    elif line.find("$metadata-name$") >= 0:
                        new_line = line.replace("$metadata-name$", metadata_name)
                        w_file.write(new_line)
                    elif line.find("$container-name$") >= 0:
                        new_line = line.replace("$container-name$", container_name)
                        w_file.write(new_line)
                    elif line.find("$labels-name$") >= 0:
                        new_line = line.replace("$labels-name$", labels_name)
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
        # 返回的是绝对路径的yaml 文件
        return new_yaml
    else:
        print "Not found the file."
        return None


def exe_com(command=None):
    """
    执行相应的程序
    启动了子进程去执行相应的任务以后，是由容器去处理的任务的，只要执行了相应的命令，子进程是可以关闭了的
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
        # logger.warn("The command is >> ( %s ) << and the result is: \n %s"
        #             % (command, this_output))
        # return this_output
    print "No command to exe."
    raise ValueError("No command to exe.")


def exe_com1(command=None):
    """
    执行相应的程序
    启动了子进程去执行相应的任务以后，是由容器去处理的任务的，只要执行了相应的命令，子进程是可以关闭了的
    """
    print command
    command = command['args']
    with open(os.path.join(base_path, 'ps.log'), 'w+') as log:
        if command:
            p = subprocess.Popen(args=command,
                                 stdout=log,
                                 stderr=subprocess.STDOUT,
                                 close_fds=False if platform.system() == 'Windows' else True,
                                 cwd=base_dir,
                                 shell=True)
            # this_output = p.stdout.read()
            log.flush()
            return
    print "No command to exe."
    raise ValueError("No command to exe.")


def exe_com2(command=None):
    """
    执行相应的程序
    启动了子进程去执行相应的任务以后，是由容器去处理的任务的，只要执行了相应的命令，子进程是可以关闭了的
    """
    index = int(command['index']) - 1
    command = command['args']
    with open(os.path.join(base_path, 'worker{}.log').format(index), 'w+') as log:
        if command:
            p = subprocess.Popen(args=command,
                                 stdout=log,
                                 stdin=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 close_fds=False if platform.system() == 'Windows' else True,
                                 cwd=base_dir,
                                 shell=True)
            log.flush()
    try:
        while p.poll() is None:
            time.sleep(1)
    except:
        p.terminate()
    delete_yaml()
    return



def exe_com3(command=None):
    """
    执行相应的程序
    启动了子进程去执行相应的任务以后，是由容器去处理的任务的，只要执行了相应的命令，子进程是可以关闭了的
    """
    print command
    with open(os.path.join(base_path, 'single.log'), 'w+') as log:
        if command:
            p = subprocess.Popen(args=command,
                                 stdout=log,
                                 stderr=subprocess.STDOUT,
                                 close_fds=False if platform.system() == 'Windows' else True,
                                 cwd=base_dir,
                                 shell=True)
            log.flush()
    try:
        while p.poll() is None:
            time.sleep(1)
    except:
        p.terminate()
    delete_yaml()
    return


def main_method(*args, **kwargs):
    # 配置完整的任务yaml文件
    num = 'hyw-%s-%s' % (time.strftime('%Y%m%d-%H%M%S'), os.urandom(2).encode('hex'))
    checkout_selector_name = num
    print "checkout_selector_name=", checkout_selector_name
    while True:
        # 先判断这个pod_name 是否存在
        get_command = ManageKubernets.get_all_pods()
        get_res = exe_com(command=get_command)
        pattern = re.compile(r'{}'.format(num))
        if re.search(pattern, get_res):
            logger.error("The pod >>>- %s -<<< has existed." % checkout_selector_name)
        else:
            logger.warn("The pod ( %s ) can be created." % checkout_selector_name)
            break
    # 参数准备
    framework = kwargs['framework']
    print framework
    container_name = num
    images = ['nvtf:nvtf20180307', 'caffe2:20180301', 'pytorch:pytorch20180208']
    if framework == 'tensorflow':
        index = 0
    elif framework == 'caffe2':
        index = 1
    elif framework == 'pytorch':
        index = 2
    # 这里需要更改
    image = images[index]
    args = kwargs['argument']
    print args
    logger.info("The arguments is :\n %s" % args)
    new_yaml = '{}.yaml'.format(num)
    logger.info("The new yaml is: %s" % new_yaml)
    # 获取yaml 的标准文件
    base_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "yaml", "base_job_new.yaml")
    metadata_name = num
    labels_name = num
    gpu_count = kwargs['gpu_count']
    cpu_count = kwargs['cpu_count']
    memory = kwargs['memory']
    command = kwargs['command']
    nfsdir = kwargs['mount_path']
    hyperai_jobs_dir = nfsdir
    # after_data_name = kwargs['after_data_name']
    logger.warn("The config key-important: images=%s, new_yaml=%s, base_file=%s, container_name=%s, "
                "metadata_name=%s, labels_name=%s"
                % (image, new_yaml, base_file, container_name, metadata_name, labels_name))
    yaml_file = get_new_yaml(base_file,
                             new_yaml=new_yaml,
                             arguments="%s" % args,
                             image=image,
                             command=command,
                             container_name=container_name,
                             labels_name=labels_name,
                             metadata_name=metadata_name,
                             gpu_count=gpu_count,
                             cpu_count=cpu_count,
                             memory=memory,
                             nfsdir=nfsdir,
                             hyperai_jobs_dir=hyperai_jobs_dir,
                             )
    logger.warn("Get the new yaml file: %s" % yaml_file)

    # 调用k8s相应的命令
    # 创建k8s实例对象
    k8s = ManageKubernets(yaml_file=yaml_file, pod_name=metadata_name)
    logger.warn("Create a instance of ManageKubernets: %s" % k8s)

    # 创建pod, 返回的是创建命令形式的字符串
    create_command = k8s.create_pods()
    logger.info("Return the create command: %s" % create_command)
    logger.info("Success create a pod.")
    exe_com(command=create_command)

    # 查看pod状态
    logger.info("Waitting five seconds.")
    time.sleep(6)  # 经过一段时间后 pod的状态变为running

    # @TODO 此处应该针对不同的pod状态，采用不同的处理方法。还需要进行完善。
    # 获取kubectl命令

    get_command = k8s.get_all_pods()
    logger.info("Return the get_command: %s" % get_command)
    # 返回的是所有的输出
    get_output = exe_com(command=get_command)

    # 获取所有信息 并且去取ip
    # 获取pod_name
    pod_name = k8s.get_full_pod_name(get_output, metadata_name)
    logger.info("Get the pod_name is : %s" % pod_name)
    print ">>>>>> %s " % pod_name
    print "输出： %s" % get_output
    # 将所有的名字加入列表
    pod_name_list.append(pod_name)
    print "名字的列表 % s" % pod_name_list
    data = k8s.get_mes_pod_field(pod_name, get_output)
    # 获取所有ip  将所有的ip加入列表中
    print "all: %s" % data
    all_ip.append(data['IP'])
    print "ip的列表 % s" % all_ip


def distributed(file_path, data_dir):
    # print after_data_name
    ps_ip = all_ip[0] + ':12222'
    ps_name = pod_name_list[0]
    for i, worker_ip in enumerate(all_ip):
        ip = ''
        for j, worker in enumerate(all_ip[1:]):
            if (j+1) < len(all_ip[1:]):
                ip += all_ip[j+1] + ':1222{},'.format(j+2)
            else:
                ip += all_ip[j + 1] + ':1222{}'.format(j+2)
        if i == 0:
            command0 = ManageKubernets.exe_distributed(pod_name=ps_name, file_path=file_path, job_name='ps',
                                                      task_index=0, ps_ip=ps_ip, worker_ip=ip, index=0, data_dir=data_dir)
            t = Process(target=exe_com1, args=(command0,))
            t.start()
            logger.info("第 %d成功" % i)
        else:
            command1 = ManageKubernets.exe_distributed(pod_name=pod_name_list[i], file_path=file_path, task_index=(i-1),
                                                      job_name='worker', ps_ip=ps_ip, worker_ip=ip, index=i, data_dir=data_dir)
            p = Process(target=exe_com2, args=(command1,))
            p.start()
            logger.info("第 %d成功" % i)


def single():
    pod_name = pod_name_list[0]
    print pod_name
    command = ManageKubernets.exe_single(pod_name)
    if command:
        t = Process(target=exe_com3, args=(command,))
        t.start()
        logger.info('单机执行成功')


def delete_yaml():
    print new_yaml_list
    for yaml in new_yaml_list:
        command2 = ManageKubernets.delete_by_yaml(yaml)
        exe_com(command2)


if __name__ == "__main__":
    """
    准备好的task通过subprocess.Popen将对应的参数
    """
    parse = argparse.ArgumentParser()
    # 这里 -a 和 -- 都可以 只是-a 是简写而已
    parse.add_argument('-a', '--argument', default=None, help="task_argument")
    # 接受传过来的参数 是一个字典
    args = vars(parse.parse_args())
    print '接受过来的参数：%s' % args
    logger.info("The argument is: \n %s" % args['argument'])
    args['argument'] = eval(args['argument'])

    node_count = args['argument'][0]
    node_count = int(node_count.split('=')[1]) + 1

    cpu_count = args['argument'][1]
    cpu_count = cpu_count.split('=')[1]

    gpu_count = args['argument'][2]
    gpu_count = int(gpu_count.split('=')[1])

    memory = args['argument'][3]
    memory = memory.split('=')[1]
    memory = '{}Gi'.format(memory)

    file_path = args['argument'][4]
    file_path = file_path.split('=')[1]

    job_id = args['argument'][5]
    job_id = job_id.split('=')[1]

    framework = args['argument'][6]
    framework = framework.split('=')[1]

    mount_path = args['argument'][7]
    mount_path = mount_path.split('=')[1]

    base_path = os.path.join(base_path, str(job_id))
    if not os.path.exists(base_path):
        os.mkdir(base_path)

    if node_count <= 1:
        data_dir = args['argument'][9]
        data_dir = data_dir.split('=')[1]

        model_dir = args['argument'][8]
        model_dir = model_dir.split('=')[1]

    argument = '["/usr/sbin/sshd -D"]'
    command = '["sh", "-c"]'
    if node_count >= 2:
        data_dir = args['argument'][8]
        data_dir = data_dir.split('=')[1]
        print node_count
        for i in range(node_count):
            if framework == 'tensorflow':
                # if i == 0:
                #     main_method(argument=argument, gpu_count=0, cpu_count=cpu_count, memory=memory,
                #                 command=command, framework=framework, mount_path=mount_path)
                # else:
                main_method(argument=argument, gpu_count=gpu_count, cpu_count=cpu_count, memory=memory,
                            command=command, framework=framework, mount_path=mount_path)
            elif framework == 'caffe2':
                pass
        distributed(file_path, data_dir)
        logger.info('分布式训练成功')
    else:
        command = '["/usr/bin/python2"]'
        if framework == 'tensorflow':
            print args['argument'][-2:]
            print file_path
            argument = args['argument'][-2:]
            argument.insert(0, file_path)
            print argument
        elif framework == 'caffe2':
            # command = '["sh", "-c"]'
            argument = ['--train_data={}'.format(data_dir)]
            argument.insert(0, file_path)
        elif framework == 'pytorch':
            print type(file_path)
            argument = [file_path]
        main_method(argument=argument, gpu_count=gpu_count, cpu_count=cpu_count, memory=memory, command=command, framework=framework, mount_path=mount_path)
        single()


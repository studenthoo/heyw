# -*- coding: utf-8 -*-

import os
import sys
from . import option_list
from hyperai.get_number import Number

# option_list['creater'] = 'hy70'

num = Number()
jobs = os.environ.get('HYPERAI_ROOT')
if jobs is None:
    print "Not Found ENV HYPERAI_ROOT."
    print "Set The jobs: /root/hyperai"
    jobs = '/root/hyperai'
config_path = os.path.join(jobs, 'Hyperai.config')


def open_config_f():
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            lists = f.readlines()
            return lists
    else:
        raise IOError('config file {} not found!'.format(config_path))


contents = open_config_f()
for line in contents:
    line = line.strip()
    # project
    if line.startswith('hyperai_ip') and line.endswith('='):
        hyperai_ip = '127.0.0.1'
    elif line.startswith('hyperai_ip') and not line.endswith('='):
        hyperai_ip = line.split('=')[-1].strip()
    if line.startswith('hyperai_root') and line.endswith('='):
        hyperai_root = '/root/hyperai'
    elif line.startswith('hyperai_root') and not line.endswith('='):
        hyperai_root = line.split('=')[-1].strip()
    if line.startswith('hyperai_port') and line.endswith('='):
        hyperai_port = '5000'
    elif line.startswith('hyperai_port') and not line.endswith('='):
        hyperai_port = line.split('=')[-1].strip()
    if line.startswith('project_creater') and line.endswith('='):
        project_creater = 'hyperai'
    elif line.startswith('project_creater') and not line.endswith('='):
        project_creater = line.split('=')[-1].strip()

    # databases
    if line.startswith('mysql_ip') and line.endswith('='):
        mysql_ip = '127.0.0.1'
    elif line.startswith('mysql_ip') and not line.endswith('='):
        mysql_ip = line.split('=')[-1].strip()
    if line.startswith('mysql_port') and line.endswith('='):
        mysql_port = '3306'
    elif line.startswith('mysql_port') and not line.endswith('='):
        mysql_port = line.split('=')[-1].strip()
    if line.startswith('mysql_db') and line.endswith('='):
        mysql_db = 'test'
    elif line.startswith('mysql_db') and not line.endswith('='):
        mysql_db = line.split('=')[-1].strip()
    if line.startswith('mysql_user') and line.endswith('='):
        mysql_user = 'root'
    elif line.startswith('mysql_user') and not line.endswith('='):
        mysql_user = line.split('=')[-1].strip()
    if line.startswith('mysql_password') and line.endswith('='):
        mysql_password = 'root'
    elif line.startswith('mysql_password') and not line.endswith('='):
        mysql_password = line.split('=')[-1].strip()
    if line.startswith('redis_ip') and line.endswith('='):
        redis_ip = 'localhost'
    elif line.startswith('redis_ip') and not line.endswith('='):
        redis_ip = line.split('=')[-1].strip()
    if line.startswith('redis_port') and line.endswith('='):
        redis_port = '6379'
    elif line.startswith('redis_port') and not line.endswith('='):
        redis_port = line.split('=')[-1].strip()
    if line.startswith('redis_db') and line.endswith('='):
        redis_db = 0
    elif line.startswith('redis_db') and not line.endswith('='):
        redis_db = line.split('=')[-1].strip()

    # deployment
    if line.startswith('deploy_ip') and line.endswith('='):
        deploy_ip = '10.18.95.2'
    elif line.startswith('deploy_ip') and not line.endswith('='):
        deploy_ip = line.split('=')[-1].strip()

    # jupyter
    if line.startswith('jupyter_ip') and line.endswith('='):
        jupyter_ip = '10.18.95.4'
    elif line.startswith('jupyter_ip') and not line.endswith('='):
        jupyter_ip = line.split('=')[-1].strip()
    if line.startswith('jupyter_port') and line.endswith('='):
        jupyter_port = '30070'
    elif line.startswith('jupyter_port') and not line.endswith('='):
        jupyter_port = line.split('=')[-1].strip()

    # images
    if line.startswith('img_main') and line.endswith('='):
        img_main = 'tem_hy:tem_hy_70'
    elif line.startswith('img_main') and not line.endswith('='):
        img_main = line.split('=')[-1].strip()
    if line.startswith('img_deploy_tensorrt') and line.endswith('='):
        img_deploy_tensorrt = 'compile:tensort3'
    elif line.startswith('img_deploy_tensorrt') and not line.endswith('='):
        img_deploy_tensorrt = line.split('=')[-1].strip()
    if line.startswith('img_deploy_tfserving') and line.endswith('='):
        img_deploy_tfserving = 'tfserving:serving'
    elif line.startswith('img_deploy_tfserving') and not line.endswith('='):
        img_deploy_tfserving = line.split('=')[-1].strip()

    # yaml
    if line.startswith('nfs_ip') and line.endswith('='):
        nfs_ip = '10.18.95.2'
    elif line.startswith('nfs_ip') and not line.endswith('='):
        nfs_ip = line.split('=')[-1].strip()
    if line.startswith('nfs_path') and line.endswith('='):
        nfs_path = '10.18.95.2'
    elif line.startswith('nfs_path') and not line.endswith('='):
        nfs_path = line.split('=')[-1].strip()
    # if line.startswith('resources_label') and line.endswith('='):
    #     resources_label = None
    elif line.startswith('resources_label') and not line.endswith('='):
        resources_label = line.split('=')[-1].strip()

    # yaml
    if line.startswith('mail_password') and line.endswith('='):
        mail_password = 'hyper123'
    elif line.startswith('mail_password') and not line.endswith('='):
        mail_password = line.split('=')[-1].strip()
    if line.startswith('mail_username') and line.endswith('='):
        mail_username = 'hyperai_admin@163.com'
    elif line.startswith('mail_username') and not line.endswith('='):
        mail_username = line.split('=')[-1].strip()

    if line.startswith('img_mysql_ip') and line.endswith('='):
        img_mysql_ip = '10.18.101.85'
    elif line.startswith('img_mysql_ip') and not line.endswith('='):
        img_mysql_ip = line.split('=')[-1].strip()

    if line.startswith('img_mysql_port') and line.endswith('='):
        img_mysql_port = '3306'
    elif line.startswith('img_mysql_port') and not line.endswith('='):
        img_mysql_port = line.split('=')[-1].strip()

    if line.startswith('img_mysql_db') and line.endswith('='):
        img_mysql_db = 'registry'
    elif line.startswith('img_mysql_db') and not line.endswith('='):
        img_mysql_db = line.split('=')[-1].strip()

    if line.startswith('img_mysql_user') and line.endswith('='):
        img_mysql_user = 'root'
    elif line.startswith('img_mysql_user') and not line.endswith('='):
        img_mysql_user = line.split('=')[-1].strip()

    if line.startswith('img_mysql_password') and line.endswith('='):
        img_mysql_password = 'root123'
    elif line.startswith('img_mysql_password') and not line.endswith('='):
        img_mysql_password = line.split('=')[-1].strip()

    if line.startswith('img_vip_port') and line.endswith('='):
        img_vip_port = '80'
    elif line.startswith('img_vip_port') and not line.endswith('='):
        img_vip_port = line.split('=')[-1].strip()

    if line.startswith('grafana_ip') and line.endswith('='):
        grafana_ip = '10.18.95.8'
    elif line.startswith('grafana_ip') and not line.endswith('='):
        grafana_ip = line.split('=')[-1].strip()

    if line.startswith('grafana_port') and line.endswith('='):
        grafana_port = '30103'
    elif line.startswith('grafana_port') and not line.endswith('='):
        grafana_port = line.split('=')[-1].strip()



image_list={}
image_list['mpi_image'] = img_main
image_list['generic_image'] = img_main

# projcet
option_list['hyperai_ip'] = hyperai_ip
option_list['hyperai_port'] = hyperai_port
option_list['hyperai_root'] = hyperai_root
option_list['creater'] = project_creater
# databases
option_list['mysql_ip'] = mysql_ip
option_list['mysql_port'] = mysql_port
option_list['mysql_db'] = mysql_db
option_list['mysql_user'] = mysql_user
option_list['mysql_password'] = mysql_password
option_list['redis_ip'] = redis_ip
option_list['redis_port'] = int(redis_port)
option_list['redis_db'] = int(redis_db)
# deploy
option_list['deploy_ip'] = deploy_ip
# jupyter
option_list['jupyter_ip'] = jupyter_ip
option_list['jupyter_port'] = jupyter_port

option_list['gpus_init_cluster'] = num.gpus_init_cluster
option_list['gpus_max_on_nodes'] = num.gpus_max_on_nodes
# images
option_list['img_main'] = img_main
option_list['image_list'] = image_list
option_list['img_deploy_tensorrt'] = img_deploy_tensorrt
option_list['img_deploy_tfserving'] = img_deploy_tfserving
option_list['img_mysql_ip'] = img_mysql_ip
option_list['img_mysql_port'] = int(img_mysql_port)
option_list['img_mysql_db'] = img_mysql_db
option_list['img_mysql_user'] = img_mysql_user
option_list['img_mysql_password'] = img_mysql_password
option_list['img_vip_port'] = img_vip_port
# nfs
option_list['nfs_ip'] = nfs_ip
option_list['nfs_path'] = nfs_path
#mail
option_list['mail_password'] = mail_password
option_list['mail_username'] = mail_username
#grafana
option_list['grafana_port'] = grafana_port
option_list['grafana_ip'] = grafana_ip

if resources_label:
    res_list = resources_label.split(';')
    res_label = [(item.split(':')[0], int(item.split(':')[1])) for item in res_list]
    option_list['resources_label'] = res_label
else:
    raise ValueError("Not found anything about resources_label in Hyperai.config .")





#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-2017, NVIDIA CORPORATION.  All rights reserved.
from __future__ import absolute_import
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import hyperai
import flask
import os
import werkzeug
import shutil
import urllib2
import os
import random
import base64
from hyperai import dataset, extensions, model, utils, pretrained_model, vip, tuning
from flask import redirect, url_for, render_template, request, jsonify
from hyperai.ration.task.deploy_task import DeploymentTask
from .job import Deployment_job
from hyperai.config import config_value
import gevent
from hyperai.tools.deploy.kube import KubernetasCoord as k8s
from hyperai.webapp import scheduler
from hyperai import extensions, utils
from hyperai.utils.auth import requires_login
# from hyperai.ext import r
from hyperai.models import User
blueprint = flask.Blueprint(__name__, __name__)


@blueprint.route('/show', methods=['GET'])
@requires_login
def show():

    # a  =  scheduler.get_job(job_id='20180514-094827-d106')
    username = request.cookies.get('username')
    all_deployment_jobs = scheduler.get_deployment_jobs(username)
    pods_d = []
    for job in all_deployment_jobs:
        msg = job.get_status(job_id=job.id())
        if msg is None:
            dirname = os.path.join(config_value('jobs_dir'),username+'/jobs',job.id())
            if os.path.exists(dirname):
                try:
                    pass
                    shutil.rmtree(dirname)
                    scheduler.delete_job(job.id())
                except Exception as e:
                    print e
                    pass
            else:
                pass
        else:
            success = True
            # ip_pool = []
            for i in msg:
                if i[2] in ['Pending','ContainerCreating']:
                    success = False
                    job.job_status = 'Wait'
                elif i[2] == 'Running':
                    job.job_status = 'Running'
                elif i[2] in ['CreateContainerConfigError', 'CrashLoopBackOff', 'Error', 'Terminating']:
                    success = False
                    job.job_status = 'Error'
            if success == True :
                job.job_status = 'Running'
                # job.api_url = ip_pool
            pods_d.append(job)

    return flask.render_template('new/product-manage.html', index='ration',jobs=pods_d)


@blueprint.route('/new', methods=['GET'])
def new():
    gpu_node = config_value('gpus_max_on_nodes')
    return flask.render_template('new/product-train.html', index='ration',gpu_node=int(gpu_node),total_gpu_count = scheduler.ration_resources['gpus'].get_gpu_max(),remaining_gpu_count = scheduler.ration_resources['gpus'].remaining())



@blueprint.route('/check_res', methods=['GET'])
@requires_login
def check_resources():
    gpu_count = flask.request.args.get('gpu_count')
    cpu_count = flask.request.args.get('cpu_count')
    memory_count = flask.request.args.get('memory_count')
    # node_count = flask.request.args.get('node_count')
    # ismpi = flask.request.args.get('ismpi')
    username = flask.request.cookies.get('username')
    resources_deployment = flask.request.args.get('resources_deployment')
    # instance_num = flask.request.get('instance')

    if resources_deployment == '固定资源模式':
        instance_num = flask.request.args.get('input_fixation')
    elif resources_deployment == '弹性伸缩模式':
        instance_num = flask.request.args.get('instance_max')
    remaining_gpu_count = scheduler.ration_resources['gpus'].remaining()
    # check the resources about user
    gpu_total = int(gpu_count) * int(instance_num)
    if int(gpu_total) > int(remaining_gpu_count):
        data = {'a':0,'res': '当前资源池中资源信息：可用GPU/申请GPU：{}/{}'.format(int(remaining_gpu_count),int(gpu_total))}
        return flask.jsonify(data)
    else:
        return flask.jsonify({'a': 1})



@blueprint.route('/monitor', methods=['GET','POST'])
@requires_login
def monitor():
    if request.method == 'POST':
        instance_min = ''
        instance_max = ''
        replicas = 1
        version = ''
        gpu_count_min = ''
        gpu_count_max = ''
        username = request.cookies.get('username')
        deployment_name = request.form.get('deployment_name') #
        select_scence = request.values.get('select_scence')
        select_model_id = request.values.get('select_model') # digits自选model
        selected_job = scheduler.get_job(job_id=select_model_id)
        select_way = request.values.get('model_select_name')
        pic_file = request.files.get('AIP_img_updata')
        label_name = request.form.get('inference')
        if pic_file:
            pic_path_o = os.path.join(os.path.dirname(os.path.abspath(hyperai.__file__)), 'static', 'deploy_pic', pic_file.filename)
            pic_file.save(pic_path_o)
            pic_path = os.path.join('deploy_pic', pic_file.filename)
        else:
            pic_path = os.path.join('deploy_pic', 'e-1.png')
        if selected_job and select_way == 'select':
            frame = selected_job.train_task().get_framework_id()
        scene = request.values.get('scene')  # 场景选择
        if scene == 'classification' and select_way == 'upload':
            frame = request.values.get('frame') # 框架选择
            network_path = request.values.get('network_path_c')  # 网络文件路径
            model_path = request.values.get('model_path_c')  # 模型文件路径
            labels_path = request.values.get('labels_path_c')  # 标签文件路径
            model_file = request.files.get('upload_model_file_c')  # 模型文件上传
            network_file = request.files.get('upload_model_network_c')  # 网络文件上传
            labels_file = request.files.get('upload_model_labels_c')  # 标签文件上传
            select_scence = 'classification'
            # print '++++++'
        elif scene == 'image-object-detection' and select_way == 'upload':
            frame = request.values.get('frame')
            network_path = request.values.get('network_path_d')  # 网络文件路径
            model_path = request.values.get('model_path_d')  # 模型文件路径
            model_file = request.files.get('upload_model_file_d')  # 模型文件上传
            network_file = request.files.get('upload_model_network_d')  # 网络文件上传
            select_scence = 'image-object-detection'
            # print '_____'
        deployment_ways = request.values.get('deployment_ways') # 部署方式
        # if deployment_ways =='全新部署':
        version = request.form.get('version_new')
        # elif deployment_ways =='升级部署':
        #     version = request.values.get('version_update')
        model_desc = request.form.get('model_desc') # 部署容器描述
        optimization_engine = request.values.get('optimization_engine') # 优化引擎
        resources_deployment = request.values.get('resources_deployment') # 资源部署方式
        if resources_deployment == '弹性伸缩模式':
            gpu_count_min = request.form.get('gpu_count_min', '')
            gpu_count_max = request.form.get('gpu_count_max', '')
            instance_min = request.form.get('instance_min', '')
            instance_max = request.form.get('instance_max', '')
            node_count = instance_min
            # print 11111111111,instance_max,select_way,select_model_id,
        elif resources_deployment == '固定资源模式':
            replicas = request.form.get('instance', 1)
            node_count = replicas
        cpu_count = request.values.get('cpu_count')
        memory_count = request.values.get('memory_count')
        gpu_count = request.values.get('gpu_count')

        #
        # gpu_total = int(gpu_count) * int(node_count)
        # if r.get("{}_gpu".format(username)) is not None:
        #     gpu_used = r.get("{}_gpu".format(username))
        # else:
        #     gpu_used = 0
        #
        # new_gpu_used = int(gpu_used) + gpu_total
        # try:
        #     r.set("{}_gpu".format(username), new_gpu_used)
        # except Exception as e:
        #     print e

        job = Deployment_job(username=username,
                             name=deployment_name,
                             model_desc=model_desc,
                             gpu_count=gpu_count,
                             cpu_count=cpu_count,
                             memory_count=memory_count,
                             select_scence=select_scence,
                             # deployment_ways=deployment_ways,
                             resources_deployment=resources_deployment,
                             optimization_engine=optimization_engine,
                             replicas=replicas,
                             version = version,
                             instance_max=instance_max,
                             instance_min=instance_min,
                             frame=frame,
                             scene=scene,
                             job_pic=pic_path)
        # 图像分类    tensort需要执行脚本的路径
        select_model = os.path.join(config_value('jobs_dir'),username+'/jobs',job.id()) # 拼接的推理job文件路径
        if frame == 'caffe' and not select_model_id:
            if scene == 'classification':
                if all([model_file,network_file,labels_file]):
                    model_file_path = os.path.join(select_model,model_file.filename)
                    network_file_path = os.path.join(select_model,network_file.filename)
                    labels_file_path = os.path.join(select_model,labels_file.filename)
                    model_file.save(model_file_path)
                    network_file.save(network_file_path)
                    labels_file.save(labels_file_path)
                    script_file_path = pass_args(model_path=network_file_path,model_labels_path=labels_file_path,model_weight_path=model_file_path,select_model=select_model,frame=frame)
                if all([model_path,network_path,labels_path]): # 当选择caffe选择服务器路径时 3个路径都是必要的
                    if os.path.exists(model_path) and os.path.exists(network_path) and os.path.exists(labels_path):
                        script_file_path = pass_args(model_path=network_path,model_labels_path=labels_path,model_weight_path=model_path,select_model=select_model,frame=frame)
                    else:
                        return jsonify({'res':'folder is not exist'})

            elif scene == 'image-object-detection':
                model_file_name = 'model.caffemodel'
                network_file_name = 'deploy.prototxt'
                script_file_path = '/workspace/tensorrt_server/caffe_mnist'
                if all([model_file,network_file]):# 上传文件
                    model_file_path = os.path.join(select_model,'model.caffemodel')
                    old_network_file_path = os.path.join(select_model,model_file_name)
                    new_network_file_path = os.path.join(select_model,network_file_name)
                    model_file.save(model_file_path)
                    network_file.save(old_network_file_path)
                    deal_prototxt(old_network_file_path, new_network_file_path)
                    job.network_file_path = new_network_file_path
                    job.model_file_path = model_file_path
                if all([model_path,network_path]):# 服务器路径
                    if os.path.exists(model_path) and os.path.exists(network_path):
                        model_file_path = os.path.join(select_model,model_file_name)
                        network_file_path = os.path.join(select_model, network_file_name)
                        try:
                            shutil.copy(model_path,model_file_path)
                            deal_prototxt(network_path,network_file_path)
                        except Exception as e:
                            print e
                            return
                        job.network_file_path = network_file_path
                        job.model_file_path = model_file_path
        if select_model_id and select_way == 'select':
            # print 777777,select_model_id,select_scence
            if select_scence == 'classification':  # 选择digits自己训练的caffe模型时
                # select_model = os.path.join(config_value('jobs_dir'),username+'/jobs',job.id())
                script_file_path = generate_file(username, select_model, select_model_id, frame)
                job.scene = 'classification'
                # print 22222222222222222,script_file_path
            elif select_scence == 'image-object-detection':
                script_file_path = '/workspace/tensorrt_server/caffe_mnist'
                model_file_path,network_file_path = detect_file(username,select_model_id,select_model)
                job.network_file_path = network_file_path
                job.model_file_path = model_file_path
                job.scene = 'images-object-detection'

        if frame == 'tensorflow' or frame == 'onnx' and select_way == 'upload': # 选择tensorflow和onnx的时候  只需要 model文件和 label文件
            if model_path and labels_path: # 路径的方式
                if os.path.exists(model_path) and os.path.exists(labels_path):
                    script_file_path = pass_args(model_path=model_path, model_labels_path=labels_path, select_model=select_model, frame=frame)
            if model_file and model_labels_path:  # 上传的方式
                model_file_path = os.path.join(select_model,model_file.filename)
                labels_file_path = os.path.join(select_model,labels_file.filename)
                model_file.save(model_file_path)
                labels_file.save(labels_file_path)
                script_file_path = pass_args(model_path=model_file_path,model_labels_path=labels_file_path,select_model=select_model,frame=frame)


        job.tasks.append(DeploymentTask(username=username,
                                        job=job,
                                        name=deployment_name,
                                        model_desc=model_desc,
                                        gpu_count=gpu_count,
                                        cpu_count=cpu_count,
                                        memory_count=memory_count,
                                        select_model=script_file_path,
                                        select_scence=select_scence,
                                        # deployment_ways=deployment_ways,
                                        resources_deployment=resources_deployment,
                                        optimization_engine=optimization_engine,
                                        replicas=replicas,
                                        instance_max=instance_max,
                                        instance_min=instance_min,
                                        scene=scene,
                                        gpu_count_min=gpu_count_min,
                                        gpu_count_max=gpu_count_max,
                                        label_name=label_name,
                               ))
        scheduler.add_job(job)
        job.job_status = 'Waiting'
        return redirect(url_for('hyperai.ration.views.show_job',job_id=job.id()))


def deployment_show(job):
    return flask.render_template('new/product-monitoring.html', job=job)


@blueprint.route('/<job_id>.json', methods=['GET'])
@blueprint.route('/show_job/<job_id>', methods=['GET'])
@requires_login
def show_job(job_id):
    job = scheduler.get_ration_job(job_id)
    if job:
        job.job_status = 'Running'

    if job is None:
        raise werkzeug.exceptions.NotFound('Job not found')
    return deployment_show(job)


@blueprint.route('/delete_deployment/<job_id>')
@requires_login
def delete_deployment(job_id):
    job = scheduler.get_ration_job(job_id)
    job.job_status = 'Error'
    username = request.cookies.get('username')
    yaml_path = os.path.join(config_value('jobs_dir'), username+'/jobs',job_id, job_id+'.yaml')
    k8s.delete_deployment(yaml_path=yaml_path)
    # k8s.delete_svc(job_id=job_id)
    # release_res_about_user(job_id)
    job.tasks[0].relase_gpu_resoures()

    scheduler.delete_ration_job(job_id)

    return redirect(url_for('hyperai.ration.views.show'))


# 获取model的数据集的label文件
def generate_file(username,deploy_job_path,job_id,frame):
    model = scheduler.get_job(job_id) # 被选择的model
    dataset_id = model.dataset_id
    dataset_labels_path = os.path.join(config_value('jobs_dir'), username + '/jobs' ,dataset_id+'/labels.txt')
    model_labels_path = os.path.join(deploy_job_path,'labels.txt')
    selected_model_path = os.path.join(config_value('jobs_dir'), username + '/jobs', job_id)
    shutil.copy(dataset_labels_path,model_labels_path)
    old_model_path = os.path.join(selected_model_path, 'deploy.prototxt')
    new_model_path = os.path.join(deploy_job_path, 'deploy.prototxt')
    model_files = os.listdir(selected_model_path)
    old_model_weight_path = os.path.join(selected_model_path,get_model_weight(model_files))
    new_model_weight_path = os.path.join(deploy_job_path,get_model_weight(model_files))
    shutil.copy(old_model_weight_path,new_model_weight_path)
    shutil.copy(old_model_path,new_model_path)

    script_file_path = pass_args(model_path=new_model_path,
              model_labels_path=model_labels_path,
              model_weight_path=new_model_weight_path,
              select_model=deploy_job_path,
              frame=frame,
              )
    return script_file_path


def detect_file(username,select_model_id,select_model):
    model_file_name = 'model.caffemodel'
    network_file_name = 'deploy.prototxt'
    selected_model_path = os.path.join(config_value('jobs_dir'),username,'jobs',select_model_id)
    model_files = os.listdir(selected_model_path)
    old_model_path = os.path.join(selected_model_path,get_model_weight(model_files))
    new_model_path = os.path.join(select_model,model_file_name)
    shutil.copy(old_model_path,new_model_path)
    old_network_path = os.path.join(selected_model_path,network_file_name)
    new_network_path = os.path.join(select_model,network_file_name)
    deal_prototxt(old_network_path,new_network_path)
    return new_model_path,new_network_path


def pass_args(**kwargs):
    model_path = kwargs['model_path']
    model_labels_path = kwargs['model_labels_path']
    model_weight_path = kwargs.pop('model_weight_path',None)
    select_model = kwargs['select_model']
    frame = kwargs.pop('frame',None)
    if frame == 'caffe':
        template_file = os.path.join(os.path.dirname(os.path.abspath(hyperai.__file__)), 'ration', 'caffe')
        script_file_path = os.path.join(select_model,'caffe')
    elif frame == 'tensorflow':
        template_file = os.path.join(os.path.dirname(os.path.abspath(hyperai.__file__)), 'ration', 'tensorflow')
        script_file_path = os.path.join(select_model, 'tensorflow')
    elif frame == 'onnx':
        template_file = os.path.join(os.path.dirname(os.path.abspath(hyperai.__file__)), 'ration', 'onnx')
        script_file_path = os.path.join(select_model, 'onnx')
    with open(template_file,'r+') as r_file:
        with open(script_file_path,'w+') as w_file:
            for line in r_file.readlines():
                if line.find('$MODEL$') >= 0:
                    new_line = line.replace('$MODEL$',model_path)
                    w_file.write(new_line)
                elif line.find('$WEIGHTS$') >= 0:
                    new_line = line.replace('$WEIGHTS$',model_weight_path)
                    w_file.write(new_line)
                elif line.find('$LABELS$') >= 0:
                    new_line = line.replace('$LABELS$', model_labels_path)
                    w_file.write(new_line)
                else:
                    w_file.write(line)
    return script_file_path


def get_model_weight(model_files):
    b = []
    for i in model_files:
        # b = p.search(i)
        if i.split('.')[-1] == 'caffemodel':
            b.append(i.split('.')[0])

    for c in range(len(b) - 1):
        for d in range(len(b) - 1):
            if int(b[d].split('_')[-1]) < int(b[d + 1].split('_')[-1]):
                b[d], b[d + 1] = b[d + 1], b[d]
    model_weight_path = b[0]+'.caffemodel'
    return model_weight_path


@blueprint.route('/infer/<job_id>',methods=['GET','POST'])
@requires_login
def infer(job_id):
    job = scheduler.get_job(job_id)
    return render_template('/new/infer_tensorrt.html',job=job)


@blueprint.route('/classify/infer/<job_id>',methods=['GET','POST'])
@requires_login
def classify_infer(job_id):
    job = scheduler.get_job(job_id)
    if request.method == 'POST':
        # print '111111111'
        username = request.cookies.get('username')
        request_url = job.api
        count_success = job.count_success
        count_fail = job.count_fail
        file = request.files.get('data_file')
        image_path = os.path.join(config_value('jobs_dir'), username, 'infer', file.filename)
        file.save(image_path)
        length = os.path.getsize(image_path)
        # print '222222222222222',file,image_path,job.api
        b = open(image_path, 'rb')
        file_type = str(file.filename).split('.')[-1]
        request_p = urllib2.Request(url=request_url, data=b)
        request_p.add_header('Cache-Control', 'no-cache')
        request_p.add_header('Content-Length', '%d' % length)
        request_p.add_header('Content-Type', 'image/%s' % file_type)
        response = urllib2.urlopen(request_p)
        content = response.read().strip()
        # print content,file,image_path,'++++++++++++++'
        if content:
            job.count_success = count_success + 1
            job.content = eval(content)
        else:
            job.count_fail = count_fail + 1
        with open(image_path, 'r+') as f:
            out_jpg = base64.b64encode(f.read())
        output_jpg = 'data:image/%s;base64,%s' % (file_type, out_jpg)
        return render_template('/new/infer_tensorrt.html', job=job, output_jpg=output_jpg,show=True)
    elif request.method == 'GET':
        return render_template('/new/infer_tensorrt.html', job=job,show=False)


# 物体识别    jetson-inference 需要的是model和network的路径  输入图片的路径 输出图片的路径
@blueprint.route('/detect/infer/<job_id>',methods=['GET','POST'])
@requires_login
def detect_infer(job_id):
    if request.method == 'POST':
        job = scheduler.get_job(job_id)
        username = request.cookies.get('username')
        job_path = os.path.join(config_value('jobs_dir'),username,'jobs',job_id)
        msg = job.get_status(job_id=job.id()) # 获取物体识别的容器信息
        file = request.files.get('data_file')
        input_jpg_path = os.path.join(config_value('jobs_dir'),username,'infer',file.filename)
        file.save(input_jpg_path)
        name = file.filename.split('.')[0]
        output_jpg_name = ''.join([name,'_out.jpg'])
        output_jpg_path = os.path.join(config_value('jobs_dir'),username,'infer',output_jpg_name)
        network_path = job.network_file_path
        model_path =job.model_file_path
        all_pods = []
        for i in msg:
            all_pods.append(i[0])
        a = random.randint(0, len(all_pods)-1)
        pods_name = all_pods[a]
        try:
            command = 'kubectl exec -i %s -- /root/jetson-inference/build/x86_64/bin/detectnet-console  %s %s --prototxt=%s --model=%s --input_blob=data -tput_cvg=coverage --output_bbox=bboxes'%(pods_name,input_jpg_path,output_jpg_path,network_path,model_path)
            k8s.exe_command(command=str(command))

            with open(output_jpg_path,'r+') as f:
                out_jpg = base64.b64encode(f.read())
            output_jpg = 'data:image/%s;base64,%s'%('jpg',out_jpg)
            job.count_success = job.count_success + 1
        except Exception as e:
            job.count_fail = job.count_fail + 1
            return
        return render_template('/new/infer_tensorrt.html',job=job,output_jpg=output_jpg,show=True)
    elif request.method == 'GET':
        job = scheduler.get_job(job_id)
        return render_template('/new/infer_tensorrt.html',job=job,show=False)


@blueprint.route('/get_cmodel', methods=['GET','POST'])
@requires_login
def get_cmodel():
    username = flask.request.cookies.get('username')
    completed_models_old = get_job_list(model.ModelJob, False)
    completed_models = []

    for job in completed_models_old:
        if job.status.name == "Done":
            completed_models.append(job)
    user_models = []
    user = User.query.filter_by(name=username).first()
    model_m_s = user.models.all()
    for u_model in completed_models:
        if u_model.username == username and u_model.owner == True:
            user_models.append(u_model)
    for model_m in model_m_s:
        model_m_job = scheduler.get_job(model_m.job_id)
        user_models.append(model_m_job)

    user_models = list(set(user_models)) # 用户所拥有的模型
         # 用户拥有模型的个数
    model_type = flask.request.form.get('value')
    type_models = []
    for u_model in user_models: # 遍历用户模型  获取每个场景的模型
        if u_model:
            if u_model.apply_scence == model_type and u_model.status == 'D' and u_model.train_task().get_framework_id()=='caffe':
                type_models.append([u_model.name(), u_model.id()])

    length = len(type_models)
    return flask.jsonify({'length': length, 'model': type_models})



def get_job_list(cls, running):
    return sorted(
        [j for j in scheduler.get_jobs() if isinstance(j, cls) and j.status.is_running() == running],
        key=lambda j: j.status_history[0][1],
        reverse=True,
    )


def deal_prototxt(old_file_path,new_file_path):
    with open(old_file_path,'r') as old_f:
        with open(new_file_path,'w') as new_f:
            a = old_f.readlines()
            b = a[0:-12]
            for i in b:
                new_f.write(i)

# def release_res_about_user(job_id):
#     job = scheduler.get_job(job_id=job_id)
#     if job.status != 'Running':
#         username = job.username
#         gpu_num = 0
#         if job.instance_max == 0:
#             gpu_num = int(job.gpu_count)*int(job.instance_max)
#         elif job.replicas:
#             gpu_num = int(job.replicas)*int(job.gpu_count)
#         gpu_used_old = r.get("{}_gpu".format(username))
#         print ("\n* * [{id}] - release gpu about user: {name}\n  ".format(id=job.id(), name=job.username))
#         if gpu_used_old is not None:
#             gpu_used_new = (int(gpu_used_old) - gpu_num) if (int(gpu_used_old) - gpu_num) >= 0 else 0
#             r.set("{}_gpu".format(username), gpu_used_new)
#         else:
#             r.set("{}_gpu".format(username), 0)

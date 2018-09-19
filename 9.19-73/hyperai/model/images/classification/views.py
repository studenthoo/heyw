#coding=utf-8
# Copyright (c) 2014-2017, NVIDIA CORPORATION.  All rights reserved.
from __future__ import absolute_import
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import re
import tempfile
import time
import threading
import flask
import numpy as np
import werkzeug.exceptions
from datetime import datetime

from .forms import ImageClassificationModelForm
from .job import ImageClassificationModelJob
from hyperai import frameworks
from hyperai import utils
from hyperai.config import config_value
from hyperai.dataset import ImageClassificationDatasetJob
from hyperai.inference import ImageInferenceJob
from hyperai.pretrained_model.job import PretrainedModelJob
from hyperai.status import Status
from hyperai.utils import filesystem as fs
from hyperai.utils.forms import fill_form_if_cloned, save_form_to_job
from hyperai.utils.routing import request_wants_json, job_from_request
from hyperai.webapp import scheduler
from hyperai.models import User
# from hyperai.ext import r
from hyperai.utils.auth import requires_login
from hyperai.users import register_user

blueprint = flask.Blueprint(__name__, __name__)

"""
Read image list
"""


def read_image_list(image_list, image_folder, num_test_images):
    paths = []
    ground_truths = []

    for line in image_list.readlines():
        line = line.strip()
        if not line:
            continue

        # might contain a numerical label at the end
        match = re.match(r'(.*\S)\s+(\d+)$', line)
        if match:
            path = match.group(1)
            ground_truth = int(match.group(2))
        else:
            path = line
            ground_truth = None

        if not utils.is_url(path) and image_folder and not os.path.isabs(path):
            path = os.path.join(image_folder, path)
        paths.append(path)
        ground_truths.append(ground_truth)

        if num_test_images is not None and len(paths) >= num_test_images:
            break
    return paths, ground_truths


@blueprint.route('/new', methods=['GET'])
@requires_login
# @utils.auth.requires_login
def new():
    """
    Return a form for a new ImageClassificationModelJob
    """
    username = flask.request.cookies.get('username')
    form = ImageClassificationModelForm()
    form.dataset.choices = get_datasets(username)
    form.standard_networks.choices = get_standard_networks()
    form.standard_networks.default = get_default_standard_network()
    form.previous_networks.choices = get_previous_networks()
    form.pretrained_networks.choices = get_pretrained_networks()

    prev_network_snapshots = get_previous_network_snapshots()

    # Is there a request to clone a job with ?clone=<job_id>
    fill_form_if_cloned(form)
    if form.train_method.data == '1':
        mark = 'mark'
    else:
        mark = 'no_mark'
    node_label_dict = scheduler.resources['gpus'].get_usable_label_gpu()
    label_gpu_value = [v for k, v in sorted(node_label_dict.items())]
    return flask.render_template('models/images/classification/new-ABC.html',
                                 form=form,
                                 mark=mark,
                                 frameworks=frameworks.get_frameworks(),
                                 previous_network_snapshots=prev_network_snapshots,
                                 previous_networks_fullinfo=get_previous_networks_fulldetails(),
                                 pretrained_networks_fullinfo=get_pretrained_networks_fulldetails(),
                                 multi_gpu=config_value('caffe')['multi_gpu'],
                                 index='train',
                                 total_gpu_count=scheduler.resources['gpus'].get_gpu_max(),
                                 remaining_gpu_count=scheduler.resources['gpus'].remaining(),
                                 # node_label_dict=node_label_dict,
                                 usable_label_gpu_count=label_gpu_value,
                                 )


# @blueprint.route('/check_res', methods=['GET'])
# @requires_login
# def check_resources():
#     gpu_count = flask.request.args.get('gpu_count')
#     cpu_count = flask.request.args.get('cpu_count')
#     memory_count = flask.request.args.get('memory_count')
#     lr_count = flask.request.args.get('lr_count')
#     bs_count = flask.request.args.get('bs_count')
#     node_count = flask.request.args.get('node_count')
#     ismpi = flask.request.args.get('ismpi')
#     username = flask.request.cookies.get('username')
#     # print("*****************",lr_count,bs_count)
#     # print("*****************",int(lr_count),int(bs_count))
#
#     if ismpi == "0":
#         node_count = 1
#     else:
#         node_count = node_count
#
#     # check the resources about user
#     gpu_total = int(gpu_count) * int(node_count) * int(lr_count) * int(bs_count)
#     user = User.query.filter_by(name=username).first()
#     gpu_max = User.get_gpu_max(username)
#
#     if r.get("{}_gpu".format(username)) is not None:
#         gpu_used = r.get("{}_gpu".format(username))
#     else:
#         gpu_used = 0
#
#     if user:
#         if int(gpu_total) > int(gpu_max) - int(gpu_used):
#             data = {'a': 0, 'res': '您当前的资源信息：可用GPU/申请GPU：{}/{}'.format((int(gpu_max) - int(gpu_used)), int(gpu_total))}
#             return flask.jsonify(data)
#         else:
#             return flask.jsonify({'a': 1})


@blueprint.route('/check_res', methods=['GET'])
@requires_login
def check_resources():
    ismpi = flask.request.args.get('ismpi')
    username = flask.request.cookies.get('username')
    gpu_count = flask.request.args.get('gpu_count')
    # cpu_count = flask.request.args.get('cpu_count')
    # memory_count = flask.request.args.get('memory_count')
    lr_count = flask.request.args.get('lr_count')
    bs_count = flask.request.args.get('bs_count')
    node_count = flask.request.args.get('node_count')
    if ismpi == "0":
        node_count = 1
    else:
        node_count = node_count

    gpu_total = int(gpu_count) * int(node_count) * int(lr_count) * int(bs_count)
    gpu_max = User.get_gpu_max(username)

    # check the resources about user
    print('检查资源')
    res = register_user.is_enough_resource_about_user(username, gpu_total, gpu_max)
    print(res)
    if not res:
        num = register_user.get_used_resource_about_user(username)
        data = {'a': 0, 'res': '您的信息：可用GPU/申请GPU：{}/{}'.format((int(gpu_max) - num), int(gpu_total))}
        return flask.jsonify(data)
    elif res == 'Forbid':
        return flask.jsonify({'a': 0, 'res': '您已被管理员禁用，请尝试联系管理员'})
    else:
        return flask.jsonify({'a': 1})



def validate_further_resources(**kwargs):
    # gpu_max = User.get_gpu_max(username)
    # num_lr = len(sweeps)
    # num_bs = len([{'batch_size': bs} for bs in form.batch_size.data])
    # gpu_count = form.gpu_count_new.data
    # if int(gpu_count) * int(num_bs) * int(num_lr) >
    pass


@blueprint.route('.json', methods=['POST'])
@blueprint.route('', methods=['POST'], strict_slashes=False)
@requires_login
def create():
    """
    Create a new ImageClassificationModelJob

    Returns JSON when requested: {job_id,name,status} or {errors:[]}
    """
    username = flask.request.cookies.get('username')
    form = ImageClassificationModelForm()
    form.dataset.choices = get_datasets(username)
    form.standard_networks.choices = get_standard_networks()
    form.previous_networks.choices = get_previous_networks()
    form.pretrained_networks.choices = get_pretrained_networks()
    max_run_time = form.max_run_time.data
    prev_network_snapshots = get_previous_network_snapshots()
    cpu_count = form.cpu_count_more.data

    # Is there a request to clone a job with ?clone=<job_id>
    fill_form_if_cloned(form)

    if not form.validate_on_submit():
        if request_wants_json():
            return flask.jsonify({'errors': form.errors}), 400
        else:
            return flask.render_template('models/images/classification/new-ABC.html',
                                         form=form,
                                         frameworks=frameworks.get_frameworks(),
                                         previous_network_snapshots=prev_network_snapshots,
                                         previous_networks_fullinfo=get_previous_networks_fulldetails(),
                                         pretrained_networks_fullinfo=get_pretrained_networks_fulldetails(),
                                         multi_gpu=config_value('caffe')['multi_gpu'],
                                         ), 400

    datasetJob = scheduler.get_job(form.dataset.data)
    if not datasetJob:
        raise werkzeug.exceptions.BadRequest(
            'Unknown dataset job_id "%s"' % form.dataset.data)

    # sweeps will be a list of the the permutations of swept fields
    # Get swept learning_rate
    sweeps = [{'learning_rate': v} for v in form.learning_rate.data]
    add_learning_rate = len(form.learning_rate.data) > 1

    # validate further
    # gpu_max = User.get_gpu_max(username)
    # num_lr = len(sweeps)
    # num_bs = len([{'batch_size': bs} for bs in form.batch_size.data])
    # gpu_count = form.gpu_count_new.data
    # if int(gpu_count) * int(num_bs) * int(num_lr) >

    sweeps = [dict(s.items() + [('batch_size', bs)]) for bs in form.batch_size.data for s in sweeps[:]]
    add_batch_size = len(form.batch_size.data) > 1
    n_jobs = len(sweeps)

    jobs = []
    for sweep in sweeps:
        # Populate the form with swept data to be used in saving and
        # launching jobs.
        form.learning_rate.data = sweep['learning_rate']
        form.batch_size.data = sweep['batch_size']

        # Augment Job Name
        extra = ''
        if add_learning_rate:
            extra += ' learning_rate:%s' % str(form.learning_rate.data[0])
        if add_batch_size:
            extra += ' batch_size:%d' % form.batch_size.data[0]

        job = None
        try:
            job = ImageClassificationModelJob(
                username=utils.auth.get_username(),
                name=form.model_name.data + extra,
                group=form.group_name.data,
                dataset_id=datasetJob.id(),
                desc=form.model_desc.data,
                network='custom' if form.method.data == 'custom' else form.standard_networks.data,
                cpu_count=cpu_count,
            )
            # get handle to framework object

            fw = frameworks.get_framework_by_id(form.framework.data)
            pretrained_model = None
            if form.method.data == 'standard':
                found = False

                # can we find it in standard networks?
                network_desc = fw.get_standard_network_desc(form.standard_networks.data)
                if network_desc:
                    found = True
                    network = fw.get_network_from_desc(network_desc)

                if not found:
                    raise werkzeug.exceptions.BadRequest(
                        'Unknown standard model "%s"' % form.standard_networks.data)
            elif form.method.data == 'previous':
                old_job = scheduler.get_job(form.previous_networks.data)
                if not old_job:
                    raise werkzeug.exceptions.BadRequest(
                        'Job not found: %s' % form.previous_networks.data)

                use_same_dataset = (old_job.dataset_id == job.dataset_id)
                network = fw.get_network_from_previous(old_job.train_task().network, use_same_dataset)

                for choice in form.previous_networks.choices:
                    if choice[0] == form.previous_networks.data:
                        epoch = float(flask.request.form['%s-snapshot' % form.previous_networks.data])
                        if epoch == 0:
                            pass
                        elif epoch == -1:
                            pretrained_model = old_job.train_task().pretrained_model
                        else:
                            # verify snapshot exists
                            pretrained_model = old_job.train_task().get_snapshot(epoch, download=True)
                            if pretrained_model is None:
                                raise werkzeug.exceptions.BadRequest(
                                    "For the job %s, selected pretrained_model for epoch %d is invalid!"
                                    % (form.previous_networks.data, epoch))
                            # the first is the actual file if a list is returned, other should be meta data
                            if isinstance(pretrained_model, list):
                                pretrained_model = pretrained_model[0]

                            if not (os.path.exists(pretrained_model)):
                                raise werkzeug.exceptions.BadRequest(
                                    "Pretrained_model for the selected epoch doesn't exist. "
                                    "May be deleted by another user/process. "
                                    "Please restart the server to load the correct pretrained_model details.")
                            # get logical path
                            pretrained_model = old_job.train_task().get_snapshot(epoch)
                        break

            elif form.method.data == 'pretrained':
                pretrained_job = scheduler.get_job(form.pretrained_networks.data)
                model_def_path = pretrained_job.get_model_def_path()
                weights_path = pretrained_job.get_weights_path()

                network = fw.get_network_from_path(model_def_path)
                pretrained_model = weights_path

            elif form.method.data == 'custom':
                network = fw.get_network_from_desc(form.custom_network.data)
                pretrained_model = form.custom_network_snapshot.data.strip()
            else:
                raise werkzeug.exceptions.BadRequest(
                    'Unrecognized method: "%s"' % form.method.data)

            policy = {'policy': form.lr_policy.data}
            if form.lr_policy.data == 'fixed':
                pass
            elif form.lr_policy.data == 'step':
                policy['stepsize'] = form.lr_step_size.data
                policy['gamma'] = form.lr_step_gamma.data
            elif form.lr_policy.data == 'multistep':
                policy['stepvalue'] = form.lr_multistep_values.data
                policy['gamma'] = form.lr_multistep_gamma.data
            elif form.lr_policy.data == 'exp':
                policy['gamma'] = form.lr_exp_gamma.data
            elif form.lr_policy.data == 'inv':
                policy['gamma'] = form.lr_inv_gamma.data
                policy['power'] = form.lr_inv_power.data
            elif form.lr_policy.data == 'poly':
                policy['power'] = form.lr_poly_power.data
            elif form.lr_policy.data == 'sigmoid':
                policy['stepsize'] = form.lr_sigmoid_step.data
                policy['gamma'] = form.lr_sigmoid_gamma.data
            else:
                raise werkzeug.exceptions.BadRequest(
                    'Invalid learning rate policy')

            gpu_count = form.gpu_count_new_more.data
            memory_count = form.memory_count_more.data
            node_count = form.node_count.data
            node_label = form.node_label_choice.data
            # print '* node_label = ',node_label

            ismpi = form.train_method.data
            if ismpi == "0":
                gpu_count = form.gpu_count_new.data
                cpu_count = form.cpu_count.data
                memory_count = form.memory_count.data
                node_count = 1

            mpi = True


            # change the gpu_used about user
            # gpu_tatol = int(gpu_count) * int(node_count)
            # if r.get("{}_gpu".format(username)) is not None:
            #     gpu_used = r.get("{}_gpu".format(username))
            # else:
            #     gpu_used = 0
            #
            # new_gpu_used = int(gpu_used) + gpu_tatol
            # user = User.query.filter_by(name=username).first()
            # gpu_max = User.get_gpu_max(username)
            # if int(new_gpu_used) > int(gpu_max):
            #     raise ValueError("Create Job Failed: Not Enough resources about %s" % username)
            # try:
            #     r.set("{}_gpu".format(username), new_gpu_used)
            # except Exception as e:
            #     print e

            # Set up data augmentation structure
            data_aug = {}
            data_aug['flip'] = form.aug_flip.data
            data_aug['quad_rot'] = form.aug_quad_rot.data
            data_aug['rot'] = form.aug_rot.data
            data_aug['scale'] = form.aug_scale.data
            data_aug['noise'] = form.aug_noise.data
            data_aug['contrast'] = form.aug_contrast.data
            data_aug['whitening'] = form.aug_whitening.data
            data_aug['hsv_use'] = form.aug_hsv_use.data
            data_aug['hsv_h'] = form.aug_hsv_h.data
            data_aug['hsv_s'] = form.aug_hsv_s.data
            data_aug['hsv_v'] = form.aug_hsv_v.data

            # Python Layer File may be on the server or copied from the client.
            fs.copy_python_layer_file(
                bool(form.python_layer_from_client.data),
                job.dir(),
                (flask.request.files[form.python_layer_client_file.name]
                 if form.python_layer_client_file.name in flask.request.files
                 else ''), form.python_layer_server_file.data)

            job.tasks.append(fw.create_train_task(
                mpi=mpi,
                job=job,
                dataset=datasetJob,
                train_epochs=form.train_epochs.data,
                snapshot_interval=form.snapshot_interval.data,
                learning_rate=form.learning_rate.data[0],
                lr_policy=policy,
                gpu_count=int(gpu_count),
                cpu_count=int(cpu_count),
                memory_count=int(memory_count),
                node_count=int(node_count),
                node_label=node_label,
                # selected_gpus=selected_gpus,
                batch_size=form.batch_size.data[0],
                batch_accumulation=form.batch_accumulation.data,
                val_interval=form.val_interval.data,
                traces_interval=form.traces_interval.data,
                pretrained_model=pretrained_model,
                crop_size=form.crop_size.data,
                use_mean=form.use_mean.data,
                network=network,
                random_seed=form.random_seed.data,
                solver_type=form.solver_type.data,
                rms_decay=form.rms_decay.data,
                shuffle=form.shuffle.data,
                data_aug=data_aug,
                desc=form.model_desc.data
            ))

            def fun_timer():
                # if job.status.name == 'Running':
                job.abort()

            if max_run_time:
                max_run_time_second = float(max_run_time) * 60
                timer = threading.Timer(max_run_time_second, fun_timer)
                timer.start()

            job.network = form.standard_networks.data
            # Save form data with the job so we can easily clone it later.
            save_form_to_job(job, form)

            jobs.append(job)
            scheduler.add_job(job)
            if n_jobs == 1:
                if request_wants_json():
                    return flask.jsonify(job.json_dict())
                else:
                    return flask.redirect(flask.url_for('hyperai.model.views.show', job_id=job.id()))

        except:
            if job:
                scheduler.delete_job(job)
                job.release_res_about_user()
            raise

    if request_wants_json():
        return flask.jsonify(jobs=[j.json_dict() for j in jobs])

    # If there are multiple jobs launched, go to the home page.
    return flask.redirect('/index')


def show(job, related_jobs=None):
    """
    Called from hyperai.model.views.models_show()
    """
    return flask.render_template(
        'models/images/classification/show1.html',
        job=job,
        framework_ids=[
            fw.get_id()
            for fw in frameworks.get_frameworks()
        ],
        related_jobs=related_jobs
    )


@blueprint.route('/timeline_tracing', methods=['GET'])
@requires_login
def timeline_tracing():
    """
    Shows timeline trace of a model
    """
    job = job_from_request()

    return flask.render_template('models/timeline_tracing.html', job=job)


@blueprint.route('/large_graph', methods=['GET'])
@requires_login
def large_graph():
    """
    Show the loss/accuracy graph, but bigger
    """
    job = job_from_request()

    return flask.render_template('models/large_graph.html', job=job)


@blueprint.route('/classify_one.json', methods=['POST'])
@blueprint.route('/classify_one', methods=['POST', 'GET'])
@requires_login
def classify_one():
    """
    Classify one image and return the top 5 classifications
    Returns JSON when requested: {predictions: {category: confidence,...}}
    """
    username = flask.request.cookies.get('username')
    model_job = job_from_request()
    remove_image_path = False
    if 'image_path' in flask.request.form and flask.request.form['image_path']:
        image_path = flask.request.form['image_path']

    elif 'image_file' in flask.request.files and flask.request.files['image_file']:
        file = flask.request.files.get('image_file')
        file_name = file.filename.encode('utf-8')
        image_path = os.path.join(config_value('jobs_dir'), username + '/' + 'infer' + '/' + file_name)
        file.save(image_path.encode('utf-8'))
        remove_image_path = False

    else:
        raise werkzeug.exceptions.BadRequest('must provide image_path or image_file')
    epoch = None
    if 'snapshot_epoch' in flask.request.form:
        epoch = float(flask.request.form['snapshot_epoch'])
    layers = 'all'

    inference_job = ImageInferenceJob(
        username=utils.auth.get_username(),
        name="Classify One Image",
        model=model_job,
        images=[image_path],
        epoch=epoch,
        layers=layers
    )
    # schedule tasks
    scheduler.add_job(inference_job)
    # wait for job to complete
    inference_job.wait_completion()
    # retrieve inference data
    inputs, outputs, visualizations = inference_job.get_data()
    # set return status code
    status_code = 500 if inference_job.status == 'E' else 200

    # delete job
    scheduler.delete_job(inference_job)

    if remove_image_path:
        os.remove(image_path)
    image = None
    predictions = []
    if inputs is not None and len(inputs['data']) == 1:
        image = utils.image.embed_image_html(inputs['data'][0])
        # convert to class probabilities for viewing
        last_output_name, last_output_data = outputs.items()[-1]

        if len(last_output_data) == 1:
            scores = last_output_data[0].flatten()
            indices = (-scores).argsort()
            labels = model_job.train_task().get_labels()
            predictions = []
            for i in indices:

                if i < len(labels):
                    predictions.append((labels[i], scores[i]))
            predictions = [(p[0], round(100.0 * p[1], 2)) for p in predictions[:5]]

    if request_wants_json():
        return flask.jsonify({'predictions': predictions}), status_code
    else:

        return flask.render_template('models/images/classification/classify_one.html',
                                     model_job=model_job,
                                     job=inference_job,
                                     image_src=image,
                                     predictions=predictions,
                                     visualizations=visualizations,
                                     total_parameters=sum(v['param_count']
                                                          for v in visualizations if v['vis_type'] == 'Weights'),
                                     ), status_code


@blueprint.route('/classify_many.json', methods=['POST'])
@blueprint.route('/classify_many', methods=['POST', 'GET'])
@requires_login
def classify_many():
    """
    Classify many images and return the top 5 classifications for each
  对许多图像进行分类，并为每个图像返回前5个分类
    Returns JSON when requested: {classifications: {filename: [[category,confidence],...],...}}
    """
    model_job = job_from_request()
    username = flask.request.cookies.get('username')
    epoch = None  # 轮次
    if 'snapshot_epoch' in flask.request.form:
        epoch = float(flask.request.form['snapshot_epoch'])
    if 'image_folder' in flask.request.form and flask.request.form['image_folder'].strip():
        image_folder = flask.request.form['image_folder']
        if not os.path.exists(image_folder):
            raise werkzeug.exceptions.BadRequest('image_folder "%s" does not exit' % image_folder)
    else:
        image_folder = None
    if 'num_test_images' in flask.request.form and flask.request.form['num_test_images'].strip():
        num_test_images = int(flask.request.form['num_test_images'])
    else:
        num_test_images = None
    # paths, ground_truths = read_image_list(image_list, image_folder, num_test_images)
    ground_truths = []
    images_list = flask.request.files.getlist('image_list')
    if len(images_list) == 1 and images_list[0].filename.encode('utf-8').endswith('.txt'):
        image_paths, ground_truths = read_image_list(images_list[0], image_folder, num_test_images)
    else:
        image_paths = []
        if images_list:
            for file in images_list:
                file_name = file.filename.encode('utf-8')
                file.save(os.path.join(config_value('jobs_dir'), username + '/' + 'infer' + '/' + file_name))  # 创建输出图片
                # 保存图片路径
                ground_truths.append(None)
                image_path = os.path.join(config_value('jobs_dir'), username + '/' + 'infer' + '/' + file_name).encode('utf-8')
                image_paths.append(image_path)


    inference_job = ImageInferenceJob(
        username=utils.auth.get_username(),
        name="Classify Many Images",
        model=model_job,
        images=image_paths,
        epoch=epoch,
        layers='none'
    )

    # schedule tasks
    scheduler.add_job(inference_job)

    # wait for job to complete
    inference_job.wait_completion()

    # retrieve inference data
    inputs, outputs, _ = inference_job.get_data()

    # set return status code
    status_code = 500 if inference_job.status == 'E' else 200

    # delete job
    scheduler.delete_job(inference_job)

    if outputs is not None and len(outputs) < 1:
        # an error occurred
        outputs = None

    if inputs is not None:
        # retrieve path and ground truth of images that were successfully processed
        image_paths = [image_paths[idx] for idx in inputs['ids']]
        ground_truths = [ground_truths[idx] for idx in inputs['ids']]

    # defaults
    classifications = None
    show_ground_truth = None
    top1_accuracy = None
    top5_accuracy = None
    confusion_matrix = None
    per_class_accuracy = None
    labels = None

    if outputs is not None:
        # convert to class probabilities for viewing
        last_output_name, last_output_data = outputs.items()[-1]
        if len(last_output_data) < 1:
            raise werkzeug.exceptions.BadRequest(
                'Unable to classify any image from the file')

        scores = last_output_data
        # take top 5
        indices = (-scores).argsort()[:, :5]

        labels = model_job.train_task().get_labels()
        n_labels = len(labels)

        # remove invalid ground truth
        ground_truths = [x if x is not None and (0 <= x < n_labels) else None for x in ground_truths]

        # how many pieces of ground truth to we have?
        n_ground_truth = len([1 for x in ground_truths if x is not None])
        show_ground_truth = n_ground_truth > 0

        # compute classifications and statistics
        classifications = []
        n_top1_accurate = 0
        n_top5_accurate = 0
        confusion_matrix = np.zeros((n_labels, n_labels), dtype=np.dtype(int))
        for image_index, index_list in enumerate(indices):
            result = []
            if ground_truths[image_index] is not None:
                if ground_truths[image_index] == index_list[0]:
                    n_top1_accurate += 1
                if ground_truths[image_index] in index_list:
                    n_top5_accurate += 1
                if (0 <= ground_truths[image_index] < n_labels) and (0 <= index_list[0] < n_labels):
                    confusion_matrix[ground_truths[image_index], index_list[0]] += 1
            for i in index_list:
                # `i` is a category in labels and also an index into scores
                # ignore prediction if we don't have a label for the corresponding class
                # the user might have set the final fully-connected layer's num_output to
                # too high a value
                if i < len(labels):
                    result.append((labels[i], round(100.0 * scores[image_index, i], 2)))
            classifications.append(result)

        # accuracy
        if show_ground_truth:
            top1_accuracy = round(100.0 * n_top1_accurate / n_ground_truth, 2)
            top5_accuracy = round(100.0 * n_top5_accurate / n_ground_truth, 2)
            per_class_accuracy = []
            for x in xrange(n_labels):
                n_examples = sum(confusion_matrix[x])
                per_class_accuracy.append(
                    round(100.0 * confusion_matrix[x, x] / n_examples, 2) if n_examples > 0 else None)
        else:
            top1_accuracy = None
            top5_accuracy = None
            per_class_accuracy = None

        # replace ground truth indices with labels
        ground_truths = [labels[x] if x is not None and (0 <= x < n_labels) else None for x in ground_truths]

    if request_wants_json():
        joined = dict(zip(image_paths, classifications))
        return flask.jsonify({'classifications': joined}), status_code
    else:
        return flask.render_template('models/images/classification/classify_many.html',
                                     model_job=model_job,
                                     job=inference_job,
                                     paths=image_paths,
                                     classifications=classifications,
                                     show_ground_truth=show_ground_truth,
                                     ground_truths=ground_truths,
                                     top1_accuracy=top1_accuracy,
                                     top5_accuracy=top5_accuracy,
                                     confusion_matrix=confusion_matrix,
                                     per_class_accuracy=per_class_accuracy,
                                     labels=labels,
                                     ), status_code


@blueprint.route('/top_n', methods=['POST'])
@requires_login
def top_n():
    """
    Classify many images and show the top N images per category by confidence
    """
    model_job = job_from_request()

    image_list = flask.request.files['image_list']
    if not image_list:
        raise werkzeug.exceptions.BadRequest('File upload not found')

    epoch = None
    if 'snapshot_epoch' in flask.request.form:
        epoch = float(flask.request.form['snapshot_epoch'])
    if 'top_n' in flask.request.form and flask.request.form['top_n'].strip():
        top_n = int(flask.request.form['top_n'])
    else:
        top_n = 9

    if 'image_folder' in flask.request.form and flask.request.form['image_folder'].strip():
        image_folder = flask.request.form['image_folder']
        if not os.path.exists(image_folder):
            raise werkzeug.exceptions.BadRequest('image_folder "%s" does not exit' % image_folder)
    else:
        image_folder = None

    if 'num_test_images' in flask.request.form and flask.request.form['num_test_images'].strip():
        num_test_images = int(flask.request.form['num_test_images'])
    else:
        num_test_images = None

    paths, _ = read_image_list(image_list, image_folder, num_test_images)

    # create inference job
    inference_job = ImageInferenceJob(
        username=utils.auth.get_username(),
        name="TopN Image Classification",
        model=model_job,
        images=paths,
        epoch=epoch,
        layers='none'
    )

    # schedule tasks
    scheduler.add_job(inference_job)

    # wait for job to complete
    inference_job.wait_completion()

    # retrieve inference data
    inputs, outputs, _ = inference_job.get_data()

    # delete job
    scheduler.delete_job(inference_job)

    results = None
    if outputs is not None and len(outputs) > 0:
        # convert to class probabilities for viewing
        last_output_name, last_output_data = outputs.items()[-1]
        scores = last_output_data

        if scores is None:
            raise RuntimeError('An error occurred while processing the images')

        labels = model_job.train_task().get_labels()
        images = inputs['data']
        indices = (-scores).argsort(axis=0)[:top_n]
        results = []
        # Can't have more images per category than the number of images
        images_per_category = min(top_n, len(images))
        # Can't have more categories than the number of labels or the number of outputs
        n_categories = min(indices.shape[1], len(labels))
        for i in xrange(n_categories):
            result_images = []
            for j in xrange(images_per_category):
                result_images.append(images[indices[j][i]])
            results.append((
                labels[i],
                utils.image.embed_image_html(
                    utils.image.vis_square(np.array(result_images),
                                           colormap='white')
                )
            ))

    return flask.render_template('models/images/classification/top_n.html',
                                 model_job=model_job,
                                 job=inference_job,
                                 results=results,
                                 )


def get_datasets(username):
    # (j.id(), j.name())
    all_local_datasets = [ j for j in sorted(
        [j for j in scheduler.get_jobs() if isinstance(j, ImageClassificationDatasetJob) and
         (j.status.is_running() or j.status == Status.DONE)],
        cmp=lambda x, y: cmp(y.id(), x.id())
    )
     ]
    try:
        user = User.query.filter_by(name=username).first()
        dataset_m = user.datasets.all()

    except Exception as e:
        print e
        return flask.redirect('/user/login')
    user_c_datasets = []
    for data in all_local_datasets:
        if data.username == username and data.owner == True and data.status== Status.DONE:
            user_c_datasets.append(data)

    for data_m in dataset_m:

        data_m_job = scheduler.get_job(data_m.job_id)
        if isinstance(data_m_job, ImageClassificationDatasetJob) and data_m_job.status== Status.DONE:
            user_c_datasets.append(data_m_job)
    user_c_datasets = list(set(user_c_datasets))
    return [(j.id(), j.name()) for j in user_c_datasets]


def get_standard_networks():
    return [
        ('lenet', 'LeNet'),
        ('alexnet', 'AlexNet'),
        ('googlenet', 'GoogLeNet'),
        # ('squeezenet','SqueezeNet'),
        # ('inception','Inception'),
        ('vgg-16','VGG16'),
        ('resnet50', 'Resnet50'),
        ('resnet101','Resnet101'),
        ('resnet152','Resnet152'),
    ]


def get_default_standard_network():
    return 'alexnet'


def get_previous_networks():
    return [(j.id(), j.name()) for j in sorted(
        [j for j in scheduler.get_jobs() if isinstance(j, ImageClassificationModelJob)],
        cmp=lambda x, y: cmp(y.id(), x.id())
    )
    ]


def get_previous_networks_fulldetails():
    return [(j) for j in sorted(
        [j for j in scheduler.get_jobs() if isinstance(j, ImageClassificationModelJob)],
        cmp=lambda x, y: cmp(y.id(), x.id())
    )
    ]


def get_previous_network_snapshots():
    prev_network_snapshots = []
    for job_id, _ in get_previous_networks():
        job = scheduler.get_job(job_id)
        e = [(0, 'None')] + [(epoch, 'Epoch #%s' % epoch)
                             for _, epoch in reversed(job.train_task().snapshots)]
        if job.train_task().pretrained_model:
            e.insert(0, (-1, 'Previous pretrained model'))
        prev_network_snapshots.append(e)
    return prev_network_snapshots


def get_pretrained_networks():
    return [(j.id(), j.name()) for j in sorted(
        [j for j in scheduler.get_jobs() if isinstance(j, PretrainedModelJob)],
        cmp=lambda x, y: cmp(y.id(), x.id())
    )
    ]


def get_pretrained_networks_fulldetails():
    return [(j) for j in sorted(
        [j for j in scheduler.get_jobs() if isinstance(j, PretrainedModelJob)],
        cmp=lambda x, y: cmp(y.id(), x.id())
    )
    ]



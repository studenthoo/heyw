#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-2017, NVIDIA CORPORATION.  All rights reserved.
from __future__ import absolute_import

import flask
import werkzeug.exceptions

from flask import redirect, url_for
from . import images as dataset_images
from . import generic
from hyperai import extensions
from hyperai.utils.routing import job_from_request, request_wants_json
from hyperai.webapp import scheduler
from hyperai.models import User, Dataset
from hyperai.ext import db
from hyperai.config import config_value
from hyperai.utils.auth import requires_login
import os
import tarfile
import zipfile
import shutil

blueprint = flask.Blueprint(__name__, __name__)


@blueprint.route('/<job_id>.json', methods=['GET'])
@blueprint.route('/<job_id>', methods=['GET'])
@requires_login
def show(job_id):
    """
    Show a DatasetJob

    Returns JSON when requested:
        {id, name, directory, status}
    """
    job = scheduler.get_job(job_id)
    if job is None:
        raise werkzeug.exceptions.NotFound('Job not found')

    related_jobs = scheduler.get_related_jobs(job)

    if request_wants_json():
        return flask.jsonify(job.json_dict(True))
    else:
        if isinstance(job, dataset_images.ImageClassificationDatasetJob):
            return dataset_images.classification.views.show(job, related_jobs=related_jobs)
        elif isinstance(job, dataset_images.GenericImageDatasetJob):
            return dataset_images.generic.views.show(job, related_jobs=related_jobs)
        elif isinstance(job, generic.GenericDatasetJob):
            return generic.views.show(job, related_jobs=related_jobs)
        else:
            raise werkzeug.exceptions.BadRequest('Invalid job type')


@blueprint.route('/summary', methods=['GET'])
@requires_login
def summary():
    """
    Return a short HTML summary of a DatasetJob
    """
    job = job_from_request()
    if isinstance(job, dataset_images.ImageClassificationDatasetJob):
        return dataset_images.classification.views.summary(job)
    elif isinstance(job, dataset_images.GenericImageDatasetJob):
        return dataset_images.generic.views.summary(job)
    elif isinstance(job, generic.GenericDatasetJob):
        return generic.views.summary(job)
    else:
        raise werkzeug.exceptions.BadRequest('Invalid job type')


@blueprint.route('/inference-form/<extension_id>/<job_id>', methods=['GET'])
@requires_login
def inference_form(extension_id, job_id):
    """
    Returns a rendering of an inference form
    """
    inference_form_html = ""

    if extension_id != "all-default":
        extension_class = extensions.data.get_extension(extension_id)
        if not extension_class:
            raise RuntimeError("Unable to find data extension with ID=%s"
                               % job_id.dataset.extension_id)
        job = scheduler.get_job(job_id)
        if hasattr(job, 'extension_userdata'):
            extension_userdata = job.extension_userdata
        else:
            extension_userdata = {}
        extension_userdata.update({'is_inference_db': True})
        extension = extension_class(**extension_userdata)

        form = extension.get_inference_form()
        if form:
            template, context = extension.get_inference_template(form)
            inference_form_html = flask.render_template_string(template, **context)

    return inference_form_html


@blueprint.route('/publish/<job_id>', methods=['GET'])
@requires_login
def to_store(job_id):
    job = scheduler.get_job(job_id)
    job.delete = False  # 添加进商店的数据集 delete属性变为False
    username = flask.request.cookies.get('username')
    name = job.name()
    publish_user = job.username
    desc = job.desc.encode('utf-8')
    create_time = job.create_time
    data_num = 0
    if isinstance(job, dataset_images.ImageClassificationDatasetJob):
       apply_scenes = job.job_type()
       for task in job.create_db_tasks():
           data_num = data_num + int(task.entries_count)
    elif isinstance(job, dataset_images.GenericImageDatasetJob):
       apply_scenes = 'other'
       for task in job.analyze_db_tasks():
           data_num = task.image_count
    elif isinstance(job, generic.GenericDatasetJob):
       apply_scenes = job.extension_id
       for task in job.create_db_tasks():
           data_num = data_num + int(task.entry_count)
    dataset_path = job.dir()
    job_id = job_id
    data_type = job.get_backend()
    data_num = data_num
    try:
        dataset = Dataset(name=name, publish_user=publish_user,data_num=data_num,desc=desc,data_type=data_type, apply_scenes=apply_scenes, dataset_path=dataset_path, job_id=job_id)
    except Exception as e:
        print e,'oooo'
    dataset.permissions = 'S'
    user = User.query.filter_by(name=username).first()
    v = Dataset.query.filter_by(job_id=job_id).first() #
    try:
        user.datasets.append(dataset) #
        db.session.add(user)
        if v is not None:
            # print v
            db.session.rollback()
        else:
            db.session.commit()
    except Exception as e:
        print e
    path = 'dataset'
    return flask.render_template('/new/shareShop-ModelDataShop.html', path=path)


@blueprint.route('/uploads', methods=['POST'])
@requires_login
def uploads():
    print 'upload'
    username = flask.request.cookies.get('username')
    user_data_path = '/home/nfsdir/'+username+'/data'
    compress_file = flask.request.files.get('data_file')
    compress_file_path = user_data_path+'/'+compress_file.filename.encode('utf-8')
    compress_file.save(compress_file_path.encode('utf-8'))
    path = compress_file_path.encode('utf-8')
    try:
        if compress_file_path.endswith('.zip'):
            after_data_name = compress_file_path.replace('.zip','')
            unzip_file(compress_file_path, after_data_name)
        elif compress_file_path.endswith('.tar.gz'):
            after_data_name = compress_file_path.replace('.tar.gz','')
            tar_file(compress_file_path,after_data_name)
        else:
            os.remove(compress_file_path.encode('utf-8'))
            path = '文件上传失败 请上传压缩包zip'.encode('utf-8')
    except Exception as e:
        os.remove(compress_file_path.encode('utf-8'))
        print e
        path = '文件上传失败'.encode('utf-8')

    return flask.render_template('/new/file.html', path=path)


def unzip_file(zipfilename, unziptodir):
    """
    | ##@函数目的: 解压zip文件到指定目录
    | ##@参数说明：zipfilename为zip文件路径，unziptodir为解压文件后的文件目录
    | ##@返回值：无
    | ##@函数逻辑：
    """
    if not os.path.exists(unziptodir):
        os.mkdir(unziptodir, 0777)
    zfobj = zipfile.ZipFile(zipfilename)
    for name in zfobj.namelist():
        name = name.replace('\\', '/')

        if name.endswith('/'):
            p = os.path.join(unziptodir, name[:-1])
            if os.path.exists(p):
                # 如果文件夹存在，就删除之：避免有新更新无法复制
                shutil.rmtree(p)
            os.mkdir(p)
        else:
            ext_filename = os.path.join(unziptodir, name)

            ext_dir = os.path.dirname(ext_filename)
            if not os.path.exists(ext_dir):
                os.mkdir(ext_dir, 0777)
            outfile = open(ext_filename, 'wb')
            outfile.write(zfobj.read(name))
            outfile.close()


def tar_file(tarfilename, untartodir):
    """
    | ##@函数目的: 解压zip文件到指定目录
    | ##@参数说明：zipfilename为zip文件路径，unziptodir为解压文件后的文件目录
    | ##@返回值：无
    | ##@函数逻辑：
    """
    if not os.path.exists(untartodir):
        os.mkdir(untartodir, 0777)
    tarobj = tarfile.TarFile(tarfilename)
    for name in tarobj.namelist():
        name = name.replace('\\', '/')

        if name.endswith('/'):
            p = os.path.join(untartodir, name[:-1])
            if os.path.exists(p):
                # 如果文件夹存在，就删除之：避免有新更新无法复制
                shutil.rmtree(p)
            os.mkdir(p)
        else:
            ext_filename = os.path.join(untartodir, name)

            ext_dir = os.path.dirname(ext_filename)
            if not os.path.exists(ext_dir):
                os.mkdir(ext_dir, 0777)
            outfile = open(ext_filename, 'wb')
            outfile.write(tarobj.read(name))
            outfile.close()
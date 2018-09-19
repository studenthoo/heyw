# coding=utf-8

from __future__ import absolute_import
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import logging
import caffe_pb2
import PIL.Image
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
from hyperai import extensions, utils
from hyperai.utils.constants import COLOR_PALETTE_ATTRIBUTE
from flask import Blueprint, request, jsonify, url_for, redirect
from hyperai import utils
from hyperai.ext import db
from hyperai.models import Dataset, Model, Comment, User
from hyperai.utils.auth import requires_login
from hyperai.utils.response_code import RET
from hyperai.webapp import scheduler
from hyperai.dataset import tasks
from hyperai.utils.lmdbreader import DbReader
import random
from hyperai.utils.auth import requires_login
blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger('hyperai.store')  # 生成日志文件


@blueprint.route('/datasets', methods=['GET', 'POST'])  # 数据集商店首页
@requires_login
def show_dataset():
    # 商店展示默认按照时间降序
    size = 6
    if request.method == 'GET':  # 跳转方式进入 默认第一页
        page = int(request.form.get('num', 1))

        datasets_mysql = Dataset.query.filter_by(permissions='S').order_by(Dataset.create_time.desc()).all()
        datasets = []
        for i in datasets_mysql:
            a = scheduler.get_job(job_id=i.job_id)
            if a and a.status == 'D':
                datasets.append(i)
        length = len(datasets)
        pages = get_total_pages(size, length)  # 获取总页数
        if page == 1:
            datasets = datasets[0:size]
        else:
            datasets =datasets[(page-1)*size:(page*size)]
    elif request.method == 'POST':  # 点击页数
        page = int(request.form.get('num',1)) # 页面当前点击页码
        scence = request.form.get('select_scence','default')  # 获取场景条件
        layout = request.form.get('select_layout','default').lower() # 获取格式
        filter_dict = {}
        search = request.form.get('store_search', None)
        if scence != 'default':
            filter_dict['apply_scenes'] = scence
        if layout != 'default':
            filter_dict['data_type'] = layout
        filter_dict['permissions'] ='S'
        datasets_mysql = Dataset.query.filter_by(**filter_dict).order_by(Dataset.create_time.desc()).all()

        datasets = []
        for i in datasets_mysql:
            a = scheduler.get_job(job_id=i.job_id)
            if a and a.status == 'D':
                datasets.append(i)

        if search:
            search_datasets = []
            pattern = '.*'.join(search.encode('utf-8'))
            regex = re.compile(pattern)  #

            for s_dataset in datasets:
                if regex.search(s_dataset.name.encode('utf-8')):
                    search_datasets.append(s_dataset)
            datasets = search_datasets
        length = len(datasets)
        pages = get_total_pages(size,length)
        if page == 1:
            datasets = datasets[0:size]
        else:
            datasets =datasets[(page-1)*size:(page*size)]
    b = {'dataset': {index: dataset.to_basic_dict() for index, dataset in
                    enumerate(datasets)}, 'pages': pages}
    return jsonify(b)


def get_total_pages(size,length):
    if length%6 == 0:
        pages = length/6
    else:
        pages = (length/6)+1
    return pages


@blueprint.route('/models', methods=['GET', 'POST'])  # 模型商店首页
@requires_login
def show_model():
    size = 6
    if request.method == 'GET':  # 跳转方式进入 默认第一页
        page = 1
        models_mysql = Model.query.filter_by(permissions='S').order_by(Model.create_time.desc()).all()
        models = []
        for i in models_mysql:
            a = scheduler.get_job(job_id=i.job_id)
            if a and a.status == 'D':
                models.append(i)
        length = len(models)
        pages = get_total_pages(size, length)  # 获取总页数
        models = models[0:6]

    elif request.method == 'POST':  # 点击页数
        page = int(request.form.get('num',1))
        scence = request.form.get('select_scence','default')  # 获取场景条件
        framework = request.form.get('select_framework','default').lower()  # 获取格式
        network = request.form.get('select_network','default').lower()
        # star = request.form.get('select_pingfen')
        search = request.form.get('store_search',None)
        filter_dict = {}
        if scence != 'default':
            filter_dict['apply_scenes'] = scence
        if framework != 'default':
            filter_dict['framework'] = framework
        if network != 'default':
            if network == 'other':
                filter_dict['network'] = 'custom'
            else:
                filter_dict['network'] = network
        # if scence != 'default':
        #     filter_dict['star'] = star
        filter_dict['permissions'] = 'S'
        models_mysql = Model.query.filter_by(**filter_dict).order_by(Model.create_time.desc()).all()
        models = []
        for i in models_mysql:
            a = scheduler.get_job(job_id=i.job_id)
            if a and a.status == 'D':
                models.append(i)
        if search:
            search_models = []
            pattern = '.*'.join(search.encode('utf-8'))
            regex = re.compile(pattern)  #
            for s_model in models:
                if regex.search(s_model.name.encode('utf-8')):
                    search_models.append(s_model)
            models = search_models

        length = len(models)
        pages = get_total_pages(size, length)
        if page == 1:
            models = models[0:size]
        else:
            models = models[(page - 1) * size:(page * size)]

    b = {'model': {index: model.to_basic_dict() for index, model in
                     enumerate(models)}, 'pages': pages}
    return jsonify(b)


# @requires_login
@blueprint.route('/get_datasets', methods=['GET'])  # 数据集详情
@requires_login
def get_dataset():
    # 根据数据集的id来获取 数据集详细信息和相关评论
    id = request.args.get('id')
    job_id = request.args.get('job_id')
    job = scheduler.get_job(str(job_id))
    if job is None:
        return jsonify(errno=RET.DATAERR, errmsg='数据集已被管理员删除')
    try:
        dataset = Dataset.query.get(id)
    except Exception as e:
        logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='查询数据集错误')

    page_p = 0
    if dataset is not None:
        if job.job_type() == 'Image Classification Dataset':
            db = 'train'
            task = job.train_db_task()

            if task is None:
                raise ValueError('No create_db task for {0}'.format(db))
            if task.status != 'D':
                raise ValueError("This create_db task's status should be 'D' but is '{0}'".format(task.status))
            if task.backend != 'lmdb':
                raise ValueError("Backend is {0} while expected backend is lmdb".format(task.backend))
            db_path = job.path(task.db_name)
            labels = task.get_labels()

            size = 15
            label = None
            reader = DbReader(db_path)
            count = 0
            imgs = []

            for key, value in reader.entries():
                if count >= page_p * size:
                    datum = caffe_pb2.Datum()
                    datum.ParseFromString(value)
                    if label is None or datum.label == label:
                        if datum.encoded:
                            s = StringIO()
                            s.write(datum.data)
                            s.seek(0)
                            img = PIL.Image.open(s)
                        else:
                            import caffe.io
                            arr = caffe.io.datum_to_array(datum)
                            # CHW -> HWC
                            arr = arr.transpose((1, 2, 0))
                            if arr.shape[2] == 1:
                                # HWC -> HW
                                arr = arr[:, :, 0]
                            elif arr.shape[2] == 3:
                                # BGR -> RGB
                                # XXX see issue #59
                                arr = arr[:, :, [2, 1, 0]]
                            img = PIL.Image.fromarray(arr)
                        imgs.append(utils.image.embed_image_html(img))
                        # print imgs
                if label is None:
                    count += 1

                if len(imgs) >= size:
                    break

            info = dict()
            info['images'] = imgs
            # print imgs
            try:
                info['dataset'] = dataset.to_full_dict()
            except Exception as e:
                print e
        elif job.job_type() == 'Generic Image Dataset' or job.extension_id == 'image-sunnybrook' or job.extension_id=='text-classification':
            info = dict()
            info['images'] = None
            info['dataset'] = dataset.to_full_dict()
        else:
            db = job.path('train_db/features')
            db_path = job.path(db)
            # print db_path,123
            if (os.path.basename(db_path) == 'labels' and
                        COLOR_PALETTE_ATTRIBUTE in job.extension_userdata and
                    job.extension_userdata[COLOR_PALETTE_ATTRIBUTE]):
                # assume single-channel 8-bit palette
                # print 'step5-generic'
                palette = job.extension_userdata[COLOR_PALETTE_ATTRIBUTE]
                palette = np.array(palette).reshape((len(palette) / 3, 3)) / 255.
                # normalize input pixels to [0,1]
                # print 'step6-generic'
                norm = mpl.colors.Normalize(vmin=0, vmax=255)
                # create map
                cmap = plt.cm.ScalarMappable(norm=norm,
                                             cmap=mpl.colors.ListedColormap(palette))
                # print 'step0-generic'
            else:
                cmap = None

            # print 'step1-generic'

            page = 0
            size = 15

            reader = DbReader(db_path)
            count = 0
            imgs = []

            min_page = max(0, page - 5)
            total_entries = reader.total_entries

            max_page = min((total_entries - 1) / size, page + 5)
            pages = range(min_page, max_page + 1)
            # print 'step2-generic'
            for key, value in reader.entries():
                if count >= page * size:
                    datum = caffe_pb2.Datum()
                    datum.ParseFromString(value)
                    if not datum.encoded:
                        pass
                        #raise RuntimeError("Expected encoded database")
                    s = StringIO()
                    s.write(datum.data)
                    s.seek(0)
                    img = PIL.Image.open(s)
                    if cmap and img.mode in ['L', '1']:
                        data = np.array(img)
                        data = cmap.to_rgba(data) * 255
                        data = data.astype('uint8')
                        # keep RGB values only, remove alpha channel
                        data = data[:, :, 0:3]
                        img = PIL.Image.fromarray(data)
                    imgs.append(utils.image.embed_image_html(img))
                count += 1
                if len(imgs) >= size:
                    break
            # print 'step3-generic'
            info = dict()
            info['images'] = imgs
            # print imgs
            info['dataset'] = dataset.to_full_dict()
            # print info
            # print len(imgs)
        return jsonify(info)


@blueprint.route('/get_models', methods=['GET'])  # 模型详情
@requires_login
def get_model():
    # 根据数据集的id来获取 数据集详细信息和相关评论
    id = request.args.get('id')
    try:
        model = Model.query.get(id)
    except Exception as e:
        return jsonify(errno=RET.DATAERR, errmsg='查询模型错误')
    if model is not None:
        info = {}
        info['model'] = model.to_full_dict()
        return jsonify(info)


# @requires_login
@blueprint.route('/dataset/comments/', methods=['GET','POST'])  # 发表数据集评论
@requires_login
def data_comment():
    user_name = request.cookies.get('username')  # 获取登录用户名字
    if request.method == 'POST':
        comment_content = request.form.get('content')  # 获取发表评论内容
        comment_name = user_name  # 获取发表者的名字
        dataset_id = request.form.get('id')
        comment = Comment(comment_name=comment_name, comment_content=comment_content, dataset_id=dataset_id)
        try:
            db.session.add(comment)  # 添加到数据库
            db.session.commit()
        except Exception as e:
            logger.error(e)
            return jsonify(errno=RET.DATAERR, errmsg='存入数据错误')
        comments = Comment.query.filter_by(dataset_id=dataset_id).order_by(Comment.create_time.desc()).all()
        dataset = Dataset.query.get(dataset_id)
        num = len(comments)
        db.session.commit()

        page = 1
        if num <= 6:
            page_z = 1
        elif num%6 == 0:
            page_z = num/6
        else:
            page_z = (num//6)+1

        comment = comments[0:6]

        info = {'page_z':page_z,'comments':[com.to_dict() for com in comment]}
        return jsonify(info)
    elif request.method == 'GET':
        id = request.args.get('id')
        try:
            page = request.args.get('page',1)
        except Exception as e:
            print e
            page = 1
        comments = Comment.query.filter_by(dataset_id=id).order_by(Comment.create_time.desc()).all()
        num = len(comments)
        if num <= 6:
            page_z = 1
        elif num%6 == 0:
            page_z = num/6
        else:
            page_z = (num//6)+1
        if page == 1:
            comment = comments[0:6]
        else:
            comment = comments[6*page:6*(page+1)]
        info = {'page_z':page_z,'comments':[com.to_dict() for com in comment]}
        return jsonify(info)


# 数据集评论翻页
@blueprint.route('/get_dataset_comment',methods=['POST'])
@requires_login
def get_dataset_comment():
    id = request.form.get('id')
    page = request.form.get('num')
    page = int(page.encode('utf-8'))
    if page == 1:
       comments = Comment.query.filter_by(dataset_id=id).order_by(Comment.create_time.desc()).all()[0:6]
    else:
        comments = Comment.query.filter_by(dataset_id=id).order_by(Comment.create_time.desc()).all()
        comments= comments[(page - 1) * 6:page * 6]
    info = {'comments':[comment.to_dict() for comment in comments]}
    return jsonify(info)


# 模型评论翻页
@blueprint.route('/get_model_comment',methods=['POST'])
@requires_login
def get_model_comment():
    id = request.form.get('id')
    page = request.form.get('num')
    page = int(page.encode('utf-8'))
    if page == 1:
       comments = Comment.query.filter_by(model_id=id).order_by(Comment.create_time.desc()).all()[0:6]
    else:
        comments = Comment.query.filter_by(model_id=id).order_by(Comment.create_time.desc()).all()
        comments= comments[(page - 1) * 6:page * 6]
    info = {'comments':[comment.to_dict() for comment in comments]}
    return jsonify(info)


# 获取模型评论
# @requires_login
@blueprint.route('/model/comments/', methods=['GET','POST'])  #
@requires_login
def model_comment():
    user_name = request.cookies.get('username')  # 获取登录用户名
    if request.method == 'POST':
        comment_content = request.form.get('content')  # 获取发表评论内容
        comment_name = user_name  # 获取发表者的名字
        model_id = request.form.get('id') # model id
        comment = Comment(comment_name=comment_name, comment_content=comment_content, model_id=model_id)

        try:
            db.session.add(comment)  # 添加到数据库
            db.session.commit()  # 提交 返回成功代码 或者错误代码
        except Exception as e:
            logger.error(e)
            return jsonify(errno=RET.DATAERR, errmsg='存入评论错误')
        comments = Comment.query.filter_by(model_id=model_id).order_by(Comment.create_time.desc()).all()
        model = Model.query.get(model_id)
        num = len(comments)
        page = 1
        if num <= 6:
            page_z = 1
        elif num % 6 == 0:
            page_z = num / 6
        else:
            page_z = (num // 6) + 1
        comment = comments[0:6]
        info = {'page_z': page_z, 'comments': [com.to_dict() for com in comment]}
        return jsonify(info)
    elif request.method == 'GET':
        id = request.args.get('id')
        try:
            page = request.args.get('page',1)
        except Exception as e:
            print e
            page = 1
        comments = Comment.query.filter_by(model_id=id).order_by(Comment.create_time.desc()).all()
        num = len(comments)
        if num <= 6:
            page_z = 1
        elif num%6 == 0:
            page_z = num/6
        else:
            page_z = (num//6)+1
        if page == 1:
            comment = comments[0:6]
        else:
            comment = comments[6*page:6*(page+1)]
        info = {'page_z':page_z,'comments':[com.to_dict() for com in comment]}
        return jsonify(info)


# @requires_login
@blueprint.route('/dataset/buy/', methods=['POST'])
@requires_login
def buy_dataset():
    """数据集只读 所以购买可以只用同一个路径下的文件"""
    username = request.cookies.get('username')  # 获取登录用户id
    dataset_id = request.form.get('id')
    dataset = Dataset.query.get(dataset_id)
    job_id = dataset.job_id
    buy_num = int(dataset.buy_num) + 1
    user = User.query.filter_by(name=username).first()
    try:
        # a = User.query.filter_by(name=username,dataset_id=dataset_id).first()
        dataset_list = user.datasets.all()
        print dataset_id, '---->1'
        for i in dataset_list:
            print i.job_id
            if i.job_id == dataset.job_id:
                return jsonify({'res': 2})
                # print dataset_id
    except Exception as e:
        print e
    try:
        dataset.buy_num = buy_num
        user.datasets.append(dataset)
        db.session.commit()
    except Exception as e:
        logger.error(e)
        print e
    return jsonify({'res':'ok'})


# @requires_login
@blueprint.route('/model/buy/', methods=['POST'])
@requires_login
def buy_model():
    """数据集只读 所以购买可以只用同一个路径下的文件"""
    username = request.cookies.get('username')  # 获取登录用户id
    model_id = request.form.get('id')
    model = Model.query.get(model_id)
    buy_num = int(model.buy_num) + 1
    user = User.query.filter_by(name=username).first()
    # print user
    try:
        # a = User.query.filter_by(name=username,dataset_id=dataset_id).first()
        model_list = user.models.all()
        print model_id, '---->1'
        for i in model_list:
            # print i.job_id
            if i.job_id == model.job_id:
                return jsonify({'res': 2})
                # print dataset_id
    except Exception as e:
        print e
    try:
        model.buy_num = buy_num
        user.models.append(model)
        db.session.commit()
    except Exception as e:
        logger.error(e)
        print e
    return jsonify({'res':'ok'})


@blueprint.route('/dataset_pic', methods=['GET'])
@requires_login
def dataset_pic():
    """
    Returns a gallery consisting of the images of one of the dbs
    """
    job_id = request.args.get('job_id')
    job = scheduler.get_job(job_id)
    # Get LMDB
    db = flask.request.args.get('db', 'train')
    if 'train' in db.lower():
        task = job.train_db_task()
    elif 'val' in db.lower():
        task = job.val_db_task()
    elif 'test' in db.lower():
        task = job.test_db_task()
    if task is None:
        raise ValueError('No create_db task for {0}'.format(db))
    if task.status != 'D':
        raise ValueError("This create_db task's status should be 'D' but is '{0}'".format(task.status))
    if task.backend != 'lmdb':
        raise ValueError("Backend is {0} while expected backend is lmdb".format(task.backend))
    db_path = job.path(task.db_name)
    labels = task.get_labels()

    page = int(flask.request.args.get('page', 0))
    size = int(flask.request.args.get('size', 15))
    label = flask.request.args.get('label', None)

    if label is not None:
        try:
            label = int(label)
        except ValueError:
            label = None

    reader = DbReader(db_path)
    count = 0
    imgs = []

    min_page = max(0, page - 5)
    if label is None:
        total_entries = reader.total_entries
    else:
        total_entries = task.distribution[str(label)]['count']

    max_page = min((total_entries - 1) / size, page + 5)
    pages = range(min_page, max_page + 1)
    for key, value in reader.entries():
        if count >= page * size:
            datum = caffe_pb2.Datum()
            datum.ParseFromString(value)
            if label is None or datum.label == label:
                if datum.encoded:
                    s = StringIO()
                    s.write(datum.data)
                    s.seek(0)
                    img = PIL.Image.open(s)
                else:
                    import caffe.io
                    arr = caffe.io.datum_to_array(datum)
                    # CHW -> HWC
                    arr = arr.transpose((1, 2, 0))
                    if arr.shape[2] == 1:
                        # HWC -> HW
                        arr = arr[:, :, 0]
                    elif arr.shape[2] == 3:
                        # BGR -> RGB
                        # XXX see issue #59
                        arr = arr[:, :, [2, 1, 0]]
                    img = PIL.Image.fromarray(arr)
                imgs.append(utils.image.embed_image_html(img))
        if label is None:
            count += 1
        else:
            datum = caffe_pb2.Datum()
            datum.ParseFromString(value)
            if datum.label == int(label):
                count += 1
        if len(imgs) >= size:
            break
    return jsonify({'images':imgs})
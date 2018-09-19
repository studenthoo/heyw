# coding=utf-8

from __future__ import absolute_import
import os
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
blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger('hyperai.store')  # 生成日志文件


@blueprint.route('/datasets', methods=['GET', 'POST'])  # 数据集商店首页
def show_dataset():
    # 商店展示默认按照时间降序
    if request.method == 'GET':  # 跳转方式进入 默认第一页
        page = 1
    elif request.method == 'POST':  # 点击页数
        page = int(request.form.get('page'))
    try:
        if page == 1:
            datasets = Dataset.query.filter_by(permissions='S').order_by(Dataset.create_time.desc()).all()[0:6]
        else:
            datasets = Dataset.query.filter_by(permissions='S').order_by(Dataset.create_time.desc()).all()[(page - 1) * 6:(page * 6)]

    except Exception as e:
        logger.error(e)
        return None
    else:
        print len(datasets)
        if len(datasets) % 6 == 0:
            a = len(datasets) / 6
        else:
            a = len(datasets) / 6 + 1

        b = {'dataset': {index: dataset.to_basic_dict() for index, dataset in
                        enumerate(datasets)}, 'pages': a}
        # print b
        return jsonify(b)


@blueprint.route('/models', methods=['GET', 'POST'])  # 模型商店首页
def show_model():
    # if request.method == 'GET':  # 页面跳转过来（第一次）
    #     # 商店展示默认按时间降序
    #     try:
    #         models = Model.query.filter(permission='S').order_by(Model.create_time.desc()).limit(6)
    #     except Exception as e:
    #         logger.error(e)
    #         return jsonify(errno=RET.DATAERR, errmsg='查询错误')
    # elif request.method == 'POST':  # 传递参数的时候
    if request.method == 'GET':  # 跳转方式进入 默认第一页
        page = 1
    elif request.method == 'POST':  # 点击页数
        page = int(request.form.get('page'))

        # apply_scenes = request.form.get('apply_scenes')
        # framework = request.form.get('framework')
        # network = request.form.get('network')
        # star = request.form.get('star')
        # if not all([page, apply_scenes, framework, network]):
        #     return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
    try:
        if page == 1:
            models = Model.query.filter_by(permissions='S').order_by(Model.create_time.desc()).all()[0:6]
        else:
            # , apply_scenes = apply_scenes, framework = framework,
            # network = network,
            # star = star
            models = Model.query.filter_by(permission='S').order_by(Model.create_time.desc()).all()[(page-1) * 6:(page * 6)]
    except Exception as e:
        logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='查询错误')
    else:

        if len(models) % 6 == 0:
            a = len(models) / 6
        else:
            a = len(models) / 6 + 1

        b = {'model': {index: model.to_basic_dict() for index, model in
                         enumerate(models)}, 'pages': a}
        return jsonify(b)
    # else:
    #     return jsonify(errno=RET.DATAERR, errmsg='查询错误')
@requires_login
# @blueprint.route('/dataset_pic_next',methods=['POST'])
@blueprint.route('/get_datasets', methods=['GET'])  # 数据集详情
def get_dataset():
    # 根据数据集的id来获取 数据集详细信息和相关评论
    id = request.args.get('id')
    job_id = request.args.get('job_id')
    job = scheduler.get_job(str(job_id))
    # page_p = 0
    try:
        dataset = Dataset.query.get(id)
    except Exception as e:
        logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='查询数据集错误')

    print 1111111111111111111
    page_p = 0
    if dataset is not None:
        if job.extension_id:
            db = job.path('train_db/labels')
            db_path = job.path(db)
            if (os.path.basename(db_path) == 'labels' and
                        COLOR_PALETTE_ATTRIBUTE in job.extension_userdata and
                    job.extension_userdata[COLOR_PALETTE_ATTRIBUTE]):
                # assume single-channel 8-bit palette
                palette = job.extension_userdata[COLOR_PALETTE_ATTRIBUTE]
                palette = np.array(palette).reshape((len(palette) / 3, 3)) / 255.
                # normalize input pixels to [0,1]
                norm = mpl.colors.Normalize(vmin=0, vmax=255)
                # create map
                cmap = plt.cm.ScalarMappable(norm=norm,
                                             cmap=mpl.colors.ListedColormap(palette))
            else:
                cmap = None
            print '*************路径判断之后'
            page = 0
            size = 15

            reader = DbReader(db_path)
            count = 0
            imgs = []

            min_page = max(0, page - 5)
            total_entries = reader.total_entries
            print 'total_entries {}'.format(total_entries)
            max_page = min((total_entries - 1) / size, page + 5)
            pages = range(min_page, max_page + 1)
            for key, value in reader.entries():
                print key,value
                print '进入循环'
                if count >= page * size:
                    datum = caffe_pb2.Datum()
                    datum.ParseFromString(value)
                    if not datum.encoded:
                        raise RuntimeError("Expected encoded database")
                    print '捕获异常'
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
                    print imgs
                count += 1

                if len(imgs) >= size:
                    break
            print imgs
            info = dict()
            info['images'] = imgs
            # print imgs
            info['dataset'] = dataset.to_full_dict()

        else:
            print 222222222222
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
                print key,value
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


        return jsonify(info)


# @blueprint.route('/dataset_pic_next111', methods=['GET', 'POST'])
# def dataset_pic_next():
#     try:
#         if page == 1:
#             comments = Comment.query.filter(dataset.id == id).order_by(Comment.create_time.desc()).all()[0:6]
#         else:
#             comments = Comment.query.filter(dataset.id == id).order_by(Comment.create_time.desc()).all()[
#                        (page - 1) * 6:(page * 6)]
#     except Exception as e:
#         logger.error(e)
#         return jsonify(errno=RET.DATAERR, errmsg='查询评论错误')






@blueprint.route('/get_models', methods=['GET'])  # 模型详情
def get_model():
    # 根据数据集的id来获取 数据集详细信息和相关评论
    id = request.args.get('id')
    # job_id = request.args.get('job_id')

    try:
        model = Model.query.get(id)
        print model
    except Exception as e:

        return jsonify(errno=RET.DATAERR, errmsg='查询模型错误')
    if model is not None:

        info = {}
        info['model'] = model.to_full_dict()


        # info['comment'] = {index: comment.to_dict() for index, comment in enumerate(comments)}
        return jsonify(info)

# 获取数据集评论
@requires_login
@blueprint.route('/dataset/comments/', methods=['GET','POST'])  # 发表数据集评论
def data_comment():
    user_name = request.cookies.get('username')  # 获取登录用户名字
    if request.method == 'POST':
        comment_content = request.form.get('content')  # 获取发表评论内容
        comment_name = user_name  # 获取发表者的名字
        comment_star = request.form.get('star')
        dataset_id = request.form.get('id')
        comment = Comment(comment_name=comment_name, comment_content=comment_content, comment_star=comment_star,
                          dataset_id=dataset_id)
        try:
            db.session.add(comment)  # 添加到数据库
            # Comment.query.filter_by(dataset_id=dataset_id)
            db.session.commit()
        except Exception as e:
            logger.error(e)
            return jsonify(errno=RET.DATAERR, errmsg='存入数据错误')
        comments = Comment.query.filter_by(dataset_id=dataset_id).order_by(Comment.create_time.desc()).all()
        sum_star = 0
        for comment in comments:
            sum_star += int(comment.comment_star)
        dataset = Dataset.query.get(dataset_id)

        num = len(comments)
        dataset.star = sum_star/num
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
        print 1212
        id = request.args.get('id')
        print id
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
@requires_login
@blueprint.route('/model/comments/', methods=['GET','POST'])  # 发表数据集评论
def model_comment():
    user_name = request.cookies.get('username')  # 获取登录用户名
    if request.method == 'POST':
        comment_content = request.form.get('content')  # 获取发表评论内容
        comment_name = user_name  # 获取发表者的名字
        comment_star = request.form.get('star') # 评分
        model_id = request.form.get('id') # model id
        comment = Comment(comment_name=comment_name, comment_content=comment_content, comment_star=comment_star,
                          model_id=model_id)

        try:
            db.session.add(comment)  # 添加到数据库
            db.session.commit()  # 提交 返回成功代码 或者错误代码
        except Exception as e:
            logger.error(e)
            return jsonify(errno=RET.DATAERR, errmsg='存入评论错误')
        comments = Comment.query.filter_by(model_id=model_id).order_by(Comment.create_time.desc()).all()
        sum_star = 0
        for comment in comments:
            sum_star += int(comment.comment_star)
        model = Model.query.get(model_id)

        num = len(comments)
        model.star = sum_star / num
        db.session.commit()

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



@requires_login
@blueprint.route('/dataset/buy/', methods=['POST'])
def buy_dataset():
    """数据集只读 所以购买可以只用同一个路径下的文件"""
    username = request.cookies.get('username')  # 获取登录用户id
    dataset_id = request.form.get('id')
    dataset = Dataset.query.get(dataset_id)
    job_id = dataset.job_id
    buy_num = int(dataset.buy_num) + 1
    user = User.query.filter_by(name=username).first()
    print username,dataset,user,buy_num
    try:
        dataset.buy_num = buy_num
        user.datasets.append(dataset)
        db.session.commit()
    except Exception as e:
        logger.error(e)
        print e
    return jsonify({'res':'ok'})

@requires_login
@blueprint.route('/model/buy/', methods=['POST'])
def buy_model():
    """数据集只读 所以购买可以只用同一个路径下的文件"""
    username = request.cookies.get('username')  # 获取登录用户id
    model_id = request.form.get('id')
    model = Model.query.get(model_id)
    buy_num = int(model.buy_num) + 1
    user = User.query.filter_by(name=username).first()
    print user
    try:
        model.buy_num = buy_num
        user.models.append(model)
        db.session.commit()
    except Exception as e:
        logger.error(e)
        print e
    return jsonify({'res':'ok'})

@blueprint.route('/dataset_pic', methods=['GET'])
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
# coding=utf-8
from __future__ import absolute_import
import os
import sys
import logging
import flask
import random
import subprocess
import os
import platform
import datetime
import time
import gevent
import signal
import locale
import threading
import re
reload(sys)
sys.setdefaultencoding('utf-8')
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
from flask import Blueprint, request, jsonify, url_for, redirect
from hyperai.utils.auth import requires_login
from hyperai.utils.auth import requires_login
from hyperai.config import config_value
from datetime import datetime
from MySQLdb import *
from io import BlockingIOError
from hyperai import utils
from hyperai.webapp import socketio, app
from hyperai.models import User
if not platform.system() == 'Windows':
    import fcntl
else:
    import gevent.os

blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger('hyperai.sysmanager')  # 生成日志文件


@blueprint.route('/show', methods=['GET', 'POST'])  # 数据集商店首页
@requires_login
def show():
    return flask.render_template('new/mirror-warehouse.html', index='sysmanager')


def connect_mysql():
    _conn_status = True
    _max_retries_count = 5
    _conn_retries_count = 0
    _conn_timeout = 5
    while _conn_status and _conn_retries_count <= _max_retries_count:
        try:
            conn = connect(host=config_value('img_mysql_ip'), port=config_value('img_mysql_port'),
                           user=config_value('img_mysql_user'), passwd=config_value('img_mysql_password'),
                           db=config_value('img_mysql_db'), charset='utf8', connect_timeout=_conn_timeout)
            _conn_status = False
            return conn
        except Exception as e:
            _conn_retries_count += 1
            # a['statu'] = e config_value('img_mysql_ip')
            print e
    return False


def close_mysql(cursor,conn):
    cursor.close()
    conn.close()
    # try:
    #     cursor.close()
    #     conn.close()
    #     return True
    # except Exception as e:
    #     return False


@blueprint.route('/load_project', methods=['GET', 'POST'])  # 数据集商店首页
@requires_login
def load_project():
    size = 10
    if request.method == 'GET':  # 跳转方式进入 默认第一页
        project_page = 1  # 页面当前点击页码
    elif request.method == 'POST':  # 点击页数
        project_page = int(request.form.get('num', 1))  # 页面当前点击页码
    try:
        # conn = connect(host=config_value('img_mysql_ip'), port=config_value('img_mysql_port'),
        #                user=config_value('img_mysql_user'), passwd=config_value('img_mysql_password'),
        #                db=config_value('img_mysql_db'), charset='utf8')
        conn = connect_mysql()
        if conn:
            cursor1 = conn.cursor()
            # sql = 'select p.name,p.project_id,pm.value,r.name,p.creation_time from project as p join project_metadata as pm on (p.project_id=pm.project_id) join project_member as pr on (p.project_id=pr.project_id) join role as r on (r.role_id=pr.role) where p.deleted=false'
            sql = 'select p.name,p.project_id,pm.value,u.username,p.creation_time from project as p join project_metadata as pm on (p.project_id=pm.project_id) join project_member as pr on (p.project_id=pr.project_id) join role as r on (r.role_id=pr.role) join user as u on (u.user_id=pr.user_id) where p.deleted=false and u.deleted=false'
            cursor1.execute(sql)
            value = cursor1.fetchall()
            project_length = len(value)
            project_pages = get_total_pages(size, project_length)
            project_list = []
            for val in value:
                project_dict = {}
                project_dict['project_name'] = val[0]
                project_dict['project_id'] = val[1]
                project_dict['access_level'] = val[2]
                project_dict['role_name'] = val[3]
                project_dict['create_time'] = val[4]
                project_list.append(project_dict)
            # conn.commit()
            close_mysql(cursor1,conn)

            if project_page == 1:
                project_list = project_list[0:size]
            else:
                project_list = project_list[(project_page - 1) * size:(project_page * size)]
            # print project_list
            users = User.query.filter_by(examined=True).order_by(User.update_time.desc()).all()
            user_list = []
            for user in users:
                user_dict = {}
                user_dict['name'] = user.name
                user_list.append(user_dict)
            return flask.jsonify({
                'errmsg': "ok",
                'project_list': project_list,
                'project_pages': project_pages,
                'user_list': user_list,
            })
        else:
            return flask.jsonify({
                'errmsg': "error",

            })
    except Exception as e:
        # pass
        print e
        return flask.jsonify({
            'errmsg': e,
            'project_list': "",
            'project_pages': "",
            'user_list': "",

        })


@blueprint.route('/add_project', methods=['GET', 'POST'])  # 数据集商店首页
@requires_login
def add_project():
    project_name = request.form.get('project_name')
    fmt = '%Y-%m-%d %a %H:%M:%S'  # 定义时间显示格式
    project_createtime = time.strftime(fmt, time.localtime(time.time()))
    public_value = request.form.get('public_value')
    user_name = request.form.get('name')
    # print user_name
    user = User.query.filter_by(name=user_name).first()
    pro_id = ""
    try:
        # conn = connect(host=config_value('img_mysql_ip'), port=config_value('img_mysql_port'), user=config_value('img_mysql_user'), passwd=config_value('img_mysql_password'), db=config_value('img_mysql_db'), charset='utf8')
        conn = connect_mysql()
        if conn:
            cursor1 = conn.cursor()
            #user
            select_user_sql = 'select user_id from user where username = "'"%s"'" ' % user_name
            # print select_user_sql
            cursor1.execute(select_user_sql)
            user_select_id = cursor1.fetchone()
            # print user_select_id
            if user_select_id is None:
                select_max_userid_sql = "select user_id from user order by user_id desc"
                cursor1.execute(select_max_userid_sql)
                value_userid = cursor1.fetchone()
                # print value_userid
                if value_userid is None:
                    user_id = 1
                else:
                    user_id = value_userid[0] + 1
                # print user_id
                insert_user_sql = 'insert into user values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)' % (user_id, "'" + user_name + "'", "'" + user.email + "'",  "'" + user.password + "'",  "'" + user.real_name + "'", "null", 0, "null", "null", 0, "current_timestamp()", "current_timestamp()")
                # print insert_user_sql
                cursor1.execute(insert_user_sql)
            else:
                user_id = user_select_id[0]

            #project
            select_max_proid_sql = "select project_id from project order by project_id desc"

            cursor1.execute(select_max_proid_sql)
            value_proid = cursor1.fetchone()
            if value_proid is None:
                pro_id = 1
            else:
                pro_id = value_proid[0]+1
            insert_pro_sql = 'insert into project values(%s, %s, %s, %s, %s, %s)'%(pro_id, user_id, "'"+project_name+"'", "current_timestamp()", "current_timestamp()", 0)
            # # sql2 = 'update project_metadata as pm set pm.deleted = true where pm.project_id = %s'%project_id
            cursor1.execute(insert_pro_sql)
            select_max_promdid_sql = "select id from project_metadata order by id desc"
            cursor1.execute(select_max_promdid_sql)
            value_id = cursor1.fetchone()
            if value_id is None:
                promd_id = 1
            else:
                promd_id = value_id[0] + 1
            insert_promd_sql = 'insert into project_metadata values(%s, %s, %s, %s, %s, %s, %s)'%(promd_id, pro_id, "'"+"public"+"'", "'"+public_value+"'", "current_timestamp()", "current_timestamp()", 0)
            cursor1.execute(insert_promd_sql)
            insert_promm_sql = 'insert into project_member values(%s, %s, %s, %s, %s)'%(pro_id, user_id, 1, "current_timestamp()", "current_timestamp()")
            cursor1.execute(insert_promm_sql)
            conn.commit()
            close_mysql(cursor1, conn)

            return flask.jsonify({
                'errmsg': "ok",
                'project_id': pro_id,
            })
        else:
            return flask.jsonify({
                'errmsg': "error",

            })
    except Exception as e:
        # pass
        print e
        return flask.jsonify({
            'errmsg': e,
            'project_id': pro_id,
        })


@blueprint.route('/sys_project', methods=['POST'])
def sys_project():
    name = request.form.get('name')
    try:
        # conn = connect(host=config_value('img_mysql_ip'), port=config_value('img_mysql_port'),
        #                user=config_value('img_mysql_user'), passwd=config_value('img_mysql_password'),
        #                db=config_value('img_mysql_db'), charset='utf8')
        conn = connect_mysql()
        if conn:
            cursor1 = conn.cursor()
            sql = "select project_id from project where name=%s"%name
            cursor1.execute(sql)
            value = cursor1.fetchone()
            close_mysql(cursor1, conn)
        else:
            return jsonify({'res': 2})  # 连接失败
    except Exception as e:
        logger.error(e)
    if value:
        return jsonify({'res': 1})  # 帐号被注册
    else:
        return jsonify({'res':0})


@blueprint.route('/project_name', methods=['POST'])  # 数据集商店首页
@requires_login
def project_name():
    project_name = request.form.get('project_name')
    try:
        # conn = connect(host=config_value('img_mysql_ip'), port=config_value('img_mysql_port'),
        #                user=config_value('img_mysql_user'), passwd=config_value('img_mysql_password'),
        #                db=config_value('img_mysql_db'), charset='utf8')
        conn = connect_mysql()
        if conn:
            cursor1 = conn.cursor()
            sql = 'select * from project where name="'"%s"'" and deleted = false' % project_name
            cursor1.execute(sql)
            value = cursor1.fetchone()
            close_mysql(cursor1, conn)
            if value is None:
                return jsonify({'res': 0})
            else:
                return jsonify({'res': 1})
        else:
            return jsonify({'res': 2})  # 连接失败
    except Exception as e:
        # pass
        print e


@blueprint.route('/delete_project', methods=['POST'])  # 删除项目
@requires_login
def delete_project():
    project_id = request.form.getlist('project_id[]')
    for pro_id in project_id:
        try:
            # conn = connect(host=config_value('img_mysql_ip'), port=config_value('img_mysql_port'), user=config_value('img_mysql_user'), passwd=config_value('img_mysql_password'), db=config_value('img_mysql_db'), charset='utf8')
            conn = connect_mysql()
            if conn:
                cursor1 = conn.cursor()
                sql = 'select project_id,name from project where project_id=%s'% pro_id
                # print sql
                cursor1.execute(sql)
                value = cursor1.fetchone()

                sql1 = 'update project as p set p.deleted = true , p.name ="'"%s"'"  where p.project_id=%s'% (value[1] +'#'+str(value[0]),pro_id)
                # print sql1
                sql2 = 'update project_metadata as pm set pm.deleted = true where pm.project_id = %s'%pro_id
                # print  sql2
                cursor1.execute(sql1)
                cursor1.execute(sql2)
                conn.commit()
                close_mysql(cursor1, conn)
            else:
                return flask.jsonify({
                    'errmsg': "error",
                })
        except Exception as e:
            print e
    return flask.jsonify({
        'errmsg': "ok",
        'project_id': project_id,
    })


@blueprint.route('/img_details', methods=['GET'])
@requires_login
def img_details():
    return flask.render_template('new/mirror.html')


@blueprint.route('/load_img', methods=['GET', 'POST'])  # 数据集商店首页
@requires_login
def load_img():
    size = 10
    project_id = request.form.get('project_id')
    name = request.form.get('name')
    if request.method == 'GET':  # 跳转方式进入 默认第一页
        img_page = 1  # 页面当前点击页码
    elif request.method == 'POST':  # 点击页数
        img_page = int(request.form.get('num', 1))  # 页面当前点击页码
    try:
        # conn = connect(host=config_value('img_mysql_ip'), port=config_value('img_mysql_port'), user=config_value('img_mysql_user'), passwd=config_value('img_mysql_password'), db=config_value('img_mysql_db'), charset='utf8')
        conn = connect_mysql()
        if conn:
            cursor1 = conn.cursor()
            sql = 'select re.repository_id,re.name,re.pull_count,re.update_time from repository as re where re.project_id=%s'%project_id
            print sql
            cursor1.execute(sql)
            value = cursor1.fetchall()
            img_length = len(value)
            img_pages = get_total_pages(size, img_length)
            img_list = []
            for val in value:
                img_dict = {}
                if name:
                    pattern = '.*'.join(name)  # Converts 'djm' to 'd.*j.*m'
                    regex = re.compile(pattern)  #
                    match_name = regex.search(val[1])
                    # print match.group()
                    if match_name:
                        # print name
                        img_dict['repository_id'] = val[0]
                        img_dict['re_name'] = val[1]
                        img_dict['pull_count'] = val[2]
                        img_dict['update_time'] = val[3]
                        img_dict['project_id'] = project_id
                        img_list.append(img_dict)
                else:
                    img_dict['repository_id'] = val[0]
                    img_dict['re_name'] = val[1]
                    img_dict['pull_count'] = val[2]
                    img_dict['update_time'] = val[3]
                    img_dict['project_id'] = project_id
                    img_list.append(img_dict)
            close_mysql(cursor1, conn)
            if img_page == 1:
                img_list = img_list[0:size]
            else:
                img_list = img_list[(img_page - 1) * size:(img_page * size)]
            return flask.jsonify({
                'errmsg': 'ok',
                'img_list': img_list,
                'img_pages': img_pages,

            })
        else:
            return flask.jsonify({
                'errmsg': "error",

            })
    except Exception as e:
        print e
        return flask.jsonify({
            'errmsg':e,
            'img_list': "",
            'img_pages': "",

        })


@blueprint.route('/delete_img', methods=['GET', 'POST'])  # 数据集商店首页
@requires_login
def delete_img():
    repository_id = request.form.getlist('repository_id[]')
    for repo_id in repository_id:
        try:
            # conn = connect(host=config_value('img_mysql_ip'), port=config_value('img_mysql_port'),
            #                user=config_value('img_mysql_user'), passwd=config_value('img_mysql_password'),
            #                db=config_value('img_mysql_db'), charset='utf8')
            conn = connect_mysql()
            if conn:
                cursor1 = conn.cursor()
                sql = 'delete from repository where repository_id =%s'%repo_id
                cursor1.execute(sql)
                conn.commit()
                close_mysql(cursor1, conn)
            else:
                return flask.jsonify({
                    'errmsg': "error",
                })
        except Exception as e:
            print e
    return flask.jsonify({
        'errmsg': "ok",
        'repository_id': repository_id,
    })


@blueprint.route('/load_local', methods=['GET', 'POST'])
@requires_login
def load_local():
    return flask.render_template('new/load-img.html', index='sysmanager')


@blueprint.route('/load_local_img', methods=['GET', 'POST'])
@requires_login
def load_local_img():
    size = 10
    name = request.form.get('name')
    if request.method == 'GET':  # 跳转方式进入 默认第一页
        img_page = 1  # 页面当前点击页码
    elif request.method == 'POST':  # 点击页数
        img_page = int(request.form.get('num', 1))  # 页面当前点击页码
    arg = ["bash %s %s" % ("/root/docker_images.sh", config_value('hyperai_ip'))]
    print arg
    env = os.environ.copy()
    p = subprocess.Popen(args=arg,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         close_fds=False if platform.system() == 'Windows' else True,
                         env=env,
                         shell=True,
                         )
    img_list = []
    try:
        for line in p.stdout.readlines():
            if line is not None:
                line = line.strip()
            if line:
                line_list = line.split(";")
                if len(line_list) == 4:
                    img_dict = {}
                    # line_list = line.split(";")
                    if line_list[0].find("registry.xhszjs.com") >= 0:
                        pass
                    else:
                        if name:
                            # print name
                            pattern = '.*'.join(name)  # Converts 'djm' to 'd.*j.*m'
                            regex = re.compile(pattern)  #
                            match_name = regex.search(line_list[0])
                            match_tag = regex.search(line_list[1])
                            # print match.group()
                            if match_name or match_tag:
                                # print name
                                img_dict['REPOSITORY'] = line_list[0]
                                img_dict['TAG'] = line_list[1]
                                img_dict['IMAGE_ID'] = line_list[2]
                                img_dict['SIZE'] = line_list[3]
                                img_list.append(img_dict)
                            if line.find("Connection to ") >= 0:
                                print "close"
                                p.send_signal(signal.SIGTERM)
                        else:
                            # print "123"
                            img_dict['REPOSITORY'] = line_list[0]
                            img_dict['TAG'] = line_list[1]
                            img_dict['IMAGE_ID'] = line_list[2]
                            img_dict['SIZE'] = line_list[3]
                            img_list.append(img_dict)
                            if line.find("Connection to ") >= 0:
                                print "close"
                                p.send_signal(signal.SIGTERM)
        p.send_signal(signal.SIGTERM)
    except Exception as e:
        # print e
        p.send_signal(signal.SIGTERM)
        # print e
    # print img_list
    if name :
        pass
    else:
        img_list.pop(0)
    img_length = len(img_list)
    print "234", img_length
    if img_page == 1:
        img_list = img_list[0:size]
    else:
        img_list = img_list[(img_page - 1) * size:(img_page * size)]
    img_pages = get_total_pages(size, img_length)
    return flask.jsonify({
        'img_list': img_list,
        'img_pages': img_pages

    })


@blueprint.route('/validation_name', methods=['GET', 'POST'])
@requires_login
def validation_name():
    file_name = request.form.get('file_name')
    try:
        # conn = connect(host=config_value('img_mysql_ip'), port=config_value('img_mysql_port'),
        #                user=config_value('img_mysql_user'), passwd=config_value('img_mysql_password'),
        #                db=config_value('img_mysql_db'), charset='utf8')
        conn = connect_mysql()
        if conn:
            cursor1 = conn.cursor()
            sql = 'select * from imgs where file_name="'"%s"'"' % file_name
            cursor1.execute(sql)
            value = cursor1.fetchone()
            close_mysql(cursor1, conn)
            if value is None:
                return jsonify({'res': 0})  # 帐号被注册
            else:
                return jsonify({'res': 1})
        else:
            return jsonify({'res': 2}) #连接失败
    except Exception as e:
        # pass
        print e



@blueprint.route('/load_add_img', methods=['GET', 'POST'])
@requires_login
def load_add_img():
    old_file_name = request.form.get('file_name')
    file_list = old_file_name.split(config_value('jobs_dir'))
    file_name = file_list[1]
    new_file_name = config_value('jobs_dir') + file_name
    msg = "正在上传"
    max_id = None
    arg = ["bash %s %s %s" % ("/root/load_img.sh", config_value('hyperai_ip'), new_file_name)]
    print arg
    env = os.environ.copy()
    p = subprocess.Popen(args=arg,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         close_fds=False if platform.system() == 'Windows' else True,
                         env=env,
                         shell=True,
                         )
    gevent.spawn(read_line,  p, msg)
    return flask.jsonify({
        'errmsg': msg,
        'pid': p.pid,
    })


def read_line(p, msg):
    while p.poll() is None:
        # for line in utils.nonblocking_readlines(p.stdout):
        for line in p.stdout.readlines():
            # print "78989",line
            if line is not None:
                line = line.strip()
            if line:
                # print line
                if line.find("Error") >= 0:
                    line_list = line.split("Error")
                    line = "Error" + line_list[1]
                    msg = line
                    msg = line
                    socketio.emit('load img',
                                  {
                                      'task': 'error',
                                      # 'update': 'accuracy_graph',
                                      'data': msg,
                                  },
                                  namespace='/loads',
                                  # room='load'
                                  )
                    if p:
                        try:
                            p.send_signal(signal.SIGTERM)
                        except Exception as e:
                            pass
                if line.find("Loaded image ID") >= 0:
                    line_list = line.split("Loaded image ID")
                    line = "Loaded image ID" + line_list[1]
                    msg = line
                    socketio.emit('load img',
                                  {
                                      'task': 'success',
                                      # 'update': 'accuracy_graph',
                                      'data': msg,
                                  },
                                  namespace='/loads',
                                  # room='load'
                                  )
                    if p:
                        try:
                            p.send_signal(signal.SIGTERM)
                        except Exception as e:
                            pass
                if line.find("Loaded image:") >= 0:
                    line_list = line.split("Loaded image:")
                    line = "Loaded image:" + line_list[1]
                    msg = line

                    socketio.emit('load img',
                                  {
                                      'task': 'success',
                                      # 'update': 'accuracy_graph',
                                      'data': msg,
                                  },
                                  namespace='/loads',
                                  # room='load'
                                  )
                    if p:
                        p.send_signal(signal.SIGTERM)
                if line.find("Connection to "+config_value('hyperai_ip')+" closed."):
                    if p:
                        try:
                            p.send_signal(signal.SIGTERM)
                        except Exception as e:
                            pass

            else:
                time.sleep(0.05)

            time.sleep(0.1)
        # if p:
        #     with app.app_context():
        #         socketio.emit('load img',
        #                       {
        #                           'task': 'running',
        #                           # 'update': 'accuracy_graph',
        #                           'data': msg,
        #                       },
        #                       namespace='/loads',
        #                       # room='load'
        #                       )
        time.sleep(0.01)


@blueprint.route('/update_tag', methods=['GET', 'POST'])  #
@requires_login
def update_tag():
    img_id = request.form.get('img_id')
    img_name = request.form.get('img_name')
    img_tag = request.form.get('img_tag')
    msg = "修改成功！"
    arg = ["bash %s %s %s %s %s" % ("/root/updata_tag.sh", config_value('hyperai_ip'), img_id, img_name, img_tag)]
    print arg
    env = os.environ.copy()
    p = subprocess.Popen(args=arg,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         close_fds=False if platform.system() == 'Windows' else True,
                         env=env,
                         shell=True,
                         )
    for line in p.stdout.readlines():
        if line.find('Error') >= 0:
            p.send_signal(signal.SIGTERM)
            msg = "镜像名称格式错误！"
            # msg = "denied: requested access to the resource is denied"
    if p:
        try:
            p.send_signal(signal.SIGTERM)
        except Exception as e:
            pass
    return flask.jsonify({
        'errmsg': msg,
    })




@blueprint.route('/push_img', methods=['GET', 'POST'])  #
@requires_login
def push_img():
    msg = "镜像正在push！"
    img_name = request.form.get('img_name')
    img_tag = request.form.get('img_tag')
    print img_name
    if re.match( r"(\d|[1-9]\d|1\d{2}|2[0-5][0-9])\.(\d|[1-9]\d|1\d{2}|2[0-5][0-9])\.(\d|[1-9]\d|1\d{2}|2[0-5][0-9])\.(\d|[1-9]\d|1\d{2}|2[0-5][0-9]):([0-9]|[1-9]\d{1,3}|[1-5]\d{4}|6[0-5]{2}[0-3][0-5])\/(\S)+\/(\S+)*",img_name):

        # print "123"
        image_list = img_name.split("/")
        # print image_list
        project_name = image_list[1]
        # print project_name
        try:
            # conn = connect(host=config_value('img_mysql_ip'), port=config_value('img_mysql_port'),
            #                user=config_value('img_mysql_user'), passwd=config_value('img_mysql_password'),
            #                db=config_value('img_mysql_db'), charset='utf8')
            conn = connect_mysql()
            if conn:
                cursor1 = conn.cursor()
                sql = 'select * from project where name="'"%s"'" and deleted=false' % project_name
                # print  sql
                cursor1.execute(sql)
                value = cursor1.fetchone()
                close_mysql(cursor1, conn)
                if value is None:
                    msg = "镜像仓库没有这个项目！"
                    return flask.jsonify({
                        'errmsg': msg,
                    })
                else:
                    arg = ["bash %s %s %s %s %s %s " % ("/root/push_img.sh", config_value('hyperai_ip'), config_value('img_mysql_ip'),config_value('img_vip_port'), img_name, img_tag)]
                    print arg
                    env = os.environ.copy()
                    b = subprocess.Popen(args=arg,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT,
                                         close_fds=False if platform.system() == 'Windows' else True,
                                         env=env,
                                         shell=True,
                                         )
                    gevent.spawn(read_lines, b, msg)
                    # for line in b.stdout.readlines():
                    #     print line
                    #     if line.find('digest:') >= 0:
                    #         b.send_signal(signal.SIGTERM)
                    #         msg = "镜像名称格式错误！"
                    #         # msg = "denied: requested access to the resource is denied"
                    # b.send_signal(signal.SIGTERM)
                    return flask.jsonify({
                        'errmsg': msg,
                    })
            else:
                return flask.jsonify({
                    'errmsg': "error",
                })
        except Exception as e:
            # pass
            print e

    else:
        # print "234"
        msg = "镜像名称格式有误！格式应为IP:PORT/project/image_name"
        return flask.jsonify({
            'errmsg': msg,
        })


def read_lines(p, msg):
    while p.poll() is None:
        # for line in utils.nonblocking_readlines(p.stdout):
        for line in p.stdout.readlines():
            # print "2345",line
            if line is not None:
                line = line.strip()
            if line:
                # print line
                if line.find('denied: requested access to the resource is denied') >= 0:
                    msg = "镜像名称或者标签输入有误！"
                    socketio.emit('push img',
                                  {
                                      'task': 'error',
                                      # 'update': 'accuracy_graph',
                                      'data': msg,
                                  },
                                  namespace='/loads',
                                  # room='push'
                                  )
                    if p:
                        try:
                            p.send_signal(signal.SIGTERM)
                        except Exception as e:
                            pass
                if line.find("digest:") >= 0:
                    msg = "镜像push成功！"
                    socketio.emit('push img',
                                  {
                                      'task': 'success',
                                      # 'update': 'accuracy_graph',
                                      'data': msg,
                                  },
                                  namespace='/loads',
                                  # room='push',
                                  )
                    # print "12323344",p.pid
                    if p:
                        try:
                            p.send_signal(signal.SIGTERM)
                        except Exception as e:
                            pass
                if line.find("Error") >= 0:
                    try:
                        line_list = line.split('unexpected')
                        msg = "镜像push失败！"+line_list[1]
                    except Exception as e:
                        msg = "镜像push失败！"
                    socketio.emit('push img',
                                  {
                                      'task': 'success',
                                      # 'update': 'accuracy_graph',
                                      'data': msg,
                                  },
                                  namespace='/loads',
                                  # room='push',
                                  )
                    # print "12323344",p.pid
                    if p:
                        try:
                            p.send_signal(signal.SIGTERM)
                        except Exception as e:
                            pass
            else:
                time.sleep(0.01)

            time.sleep(0.01)
        # if p:
        #     with app.app_context():
        #         socketio.emit('push img',
        #                       {
        #                           'task': 'running',
        #                           # 'update': 'accuracy_graph',
        #                           'data': msg,
        #                       },
        #                       namespace='/loads',
        #                       # room='push',
        #                       )
        time.sleep(0.01)


@blueprint.route('/delete_node_img', methods=['GET', 'POST'])  #
@requires_login
def delete_node_img():
    # name_tags = request.form.getlist('name_tags[]')
    msg = "删除成功！"
    img_name = request.form.get('img_name')
    img_tag = request.form.get('img_tag')
    arg = ["bash %s %s %s %s " % ("/root/delete_img.sh", config_value('hyperai_ip'), img_name, img_tag)]
    print arg
    env = os.environ.copy()
    p = subprocess.Popen(args=arg,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         close_fds=False if platform.system() == 'Windows' else True,
                         env=env,
                         shell=True,
                         )
    for line in p.stdout.readlines():
        if line.find('Error') >= 0:
            p.send_signal(signal.SIGTERM)
            msg = "镜像正在被容器使用，不可以删除！"
            # msg = "denied: requested access to the resource is denied"
    if p:
        try:
            p.send_signal(signal.SIGTERM)
        except Exception as e:
            pass
    return flask.jsonify({
        'errmsg': msg,
    })


@blueprint.route('/pull_img', methods=['GET', 'POST'])  # 数据集商店首页
@requires_login
def pull_img():
    pass


def get_total_pages(size, length):
    if length % size == 0:
        pages = length/size
    else:
        pages = (length/size)+1
    return pages
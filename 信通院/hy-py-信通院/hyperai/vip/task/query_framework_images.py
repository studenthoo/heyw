import re
import os
from hyperai.config import config_value
import sys
from MySQLdb import *
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def read_images_file(images_file_path):
    with open(images_file_path, "r+") as file:
        result_list = file.readlines()
    ret_list = []
    for li in result_list:
        li = re.sub('\n', "", li)
        li = re.sub('\s+', " ", li)
        ret_list.append(li)
    return ret_list


def regular_frame_and_version(ret_list):
    """
    :param result:the docker images result
    :return:frame and version list
    """
    frame_version_list = []
    li_dict = {}
    distributed_li_dict = {}
    tf_list = []
    tfmpi_list = []
    caffe_list = []
    caffe2_list = []
    torch_list = []
    pytorch_list = []
    single_images_list = []
    distributed_images_list = []
    caffempi_list = []
    cntk_list = []
    theano_list = []
    mxnet_list = []
    keras_list = []
    frame_list = []
    darknet_list = []
    if ret_list:
        for line in ret_list:
            image = str(line).split("/")
            frame_version_list.append(image[-1])
        for li in frame_version_list:
            if li.startswith("tensorflow_v") or li.startswith("caffe_v") or li.startswith("torch_v") \
                    or li.startswith("caffe2_v") or li.startswith("pytorch_v") or li.startswith("tensorflowmpi_v") or li.startswith("caffempi_v") or \
                    li.startswith("cntk_v") or li.startswith("theano_v") or li.startswith("mxnet_v") or li.startswith("keras_v") or li.startswith("darknet_v"):
                frame_list.append(li)
    for frame_version_li in frame_list:
        frame, version = str(frame_version_li).split("_")
        if frame == "tensorflow":
            tf_list.append(version)
            li_dict[frame] = tf_list
            distributed_li_dict[frame] = tf_list
        elif frame == "tensorflowmpi":
            tfmpi_list.append(version)
            distributed_li_dict[frame] = tfmpi_list
        elif frame == "caffe":
            caffe_list.append(version)
            li_dict[frame] = caffe_list
        elif frame == "caffe2":
            caffe2_list.append(version)
            li_dict[frame] = caffe2_list
        elif frame == "torch":
            torch_list.append(version)
            li_dict[frame] = torch_list
        elif frame == "pytorch":
            pytorch_list.append(version)
            li_dict[frame] = pytorch_list
        elif frame == "caffempi":
            caffempi_list.append(version)
            distributed_li_dict[frame] = caffempi_list
        elif frame == "cntk":
            cntk_list.append(version)
            li_dict[frame] = cntk_list
        elif frame == "theano":
            theano_list.append(version)
            li_dict[frame] = theano_list
        elif frame == "mxnet":
            mxnet_list.append(version)
            li_dict[frame] = mxnet_list
        elif frame == "keras":
            keras_list.append(version)
            li_dict[frame] = keras_list
        elif frame == "darknet":
            darknet_list.append(version)
            li_dict[frame] = darknet_list
        else:
            pass
    single_images_list.append(li_dict)
    distributed_images_list.append(distributed_li_dict)
    return single_images_list,distributed_images_list


def get_frame():
    images_file_path = os.path.join(config_value("public_dir"), 'image_version.txt')
    ret_list = read_images_file(images_file_path)
    single_list, distributed_list = regular_frame_and_version(ret_list)
    frame_version_list = {}
    frame_version_list["single_frame"] = single_list[0]
    frame_version_list["distributed_frame"] = distributed_list[0]
    return frame_version_list


# def get_framework():
#     try:
#         # conn = connect(host='10.18.10.85', port=3306, user='root', passwd='root123', db='registry', charset='utf8')
#         conn = connect(host=config_value('img_mysql_ip'), port=config_value('img_mysql_port'), user=config_value('img_mysql_user'), passwd=config_value('img_mysql_password'), db=config_value('img_mysql_db'), charset='utf8')
#         cursor1 = conn.cursor()
#         sql = 'select name from repository order by repository_id'
#         cursor1.execute(sql)
#         value = cursor1.fetchall()
#         # conn.commit()
#         cursor1.close()
#         conn.close()
#         return value
#     except Exception as e:
#         print e

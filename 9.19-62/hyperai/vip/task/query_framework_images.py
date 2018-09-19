import re
import os
from hyperai.config import config_value
import sys
from MySQLdb import *
from flask import request
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from hyperai.webapp import scheduler
import json
import datetime


def regular_frame_and_version(ret_list):
    """
    :param result:the docker images result
    :return:frame and version list
    """
    frame_version_list = []


    single_images_list = []
    distributed_images_list = []

    frame_list = []
    sing_img_list = []
    distribute_img_list = []
    if ret_list:
        for ret_list1 in ret_list:
            for k,v in ret_list1.items():
                select_frame_list = []
                sing_dict = {}
                dixtribute_dict = {}
                li_dict = {}
                tf_list = []
                tfmpi_list = []
                caffe_list = []
                caffe2_list = []
                torch_list = []
                pytorch_list = []
                caffempi_list = []
                cntk_list = []
                theano_list = []
                mxnet_list = []
                keras_list = []
                distributed_li_dict = {}
                # print v
                for line in v:
                    image = line[0].split("/")
                    li = image[-1]
                    if li.startswith("tensorflow_v") or li.startswith("caffe_v") or li.startswith("torch_v") \
                        or li.startswith("caffe2_v") or li.startswith("pytorch_v") or li.startswith("tensorflowmpi_v") or li.startswith("caffempi_v") or \
                        li.startswith("cntk_v") or li.startswith("theano_v") or li.startswith("mxnet_v") or li.startswith("keras_v"):
                        frame, version = li.split("_")
                        if frame == "tensorflow":
                            print line
                            sing_img_list.append(frame)
                            distribute_img_list.append(frame)
                            new_line = get_new_frame(line)
                            tf_list.append(new_line)
                            li_dict[frame] = tf_list
                            # select_frame_list.append(line)
                            distributed_li_dict[frame] = tf_list
                        elif frame == "tensorflowmpi":
                            distribute_img_list.append(frame)
                            new_line = get_new_frame(line)
                            tfmpi_list.append(new_line)
                            distributed_li_dict[frame] = tfmpi_list
                        elif frame == "caffe":
                            sing_img_list.append(frame)
                            new_line = get_new_frame(line)
                            caffe_list.append(new_line)
                            li_dict[frame] = caffe_list
                        elif frame == "caffe2":
                            sing_img_list.append(frame)
                            new_line = get_new_frame(line)
                            caffe2_list.append(new_line)
                            li_dict[frame] = caffe2_list
                        elif frame == "torch":
                            sing_img_list.append(frame)
                            new_line = get_new_frame(line)
                            torch_list.append(new_line)
                            li_dict[frame] = torch_list
                        elif frame == "pytorch":
                            sing_img_list.append(frame)
                            new_line = get_new_frame(line)
                            pytorch_list.append(new_line)
                            li_dict[frame] = pytorch_list
                        elif frame == "caffempi":
                            distribute_img_list.append(frame)
                            new_line = get_new_frame(line)
                            caffempi_list.append(new_line)
                            distributed_li_dict[frame] = caffempi_list
                        elif frame == "cntk":
                            sing_img_list.append(frame)
                            new_line = get_new_frame(line)
                            cntk_list.append(new_line)
                            li_dict[frame] = cntk_list
                        elif frame == "theano":
                            sing_img_list.append(frame)
                            new_line = get_new_frame(line)
                            theano_list.append(new_line)
                            li_dict[frame] = theano_list
                        elif frame == "mxnet":
                            sing_img_list.append(frame)
                            new_line = get_new_frame(line)
                            mxnet_list.append(new_line)
                            li_dict[frame] = mxnet_list
                        elif frame == "keras":
                            sing_img_list.append(frame)
                            new_line = get_new_frame(line)
                            keras_list.append(new_line)
                            li_dict[frame] = keras_list
                        else:
                            pass

                sing_dict[k] = li_dict
                single_images_list.append(sing_dict)
                dixtribute_dict[k] = distributed_li_dict
                distributed_images_list.append(dixtribute_dict)
    sing_img_list = set(sing_img_list)
    sing_list = list(sing_img_list)
    single_dict = {}
    single_dict['image'] = sing_list
    distribute_img_list = set(distribute_img_list)
    distribute_list = list(distribute_img_list)
    distribute_dict = {}
    distribute_dict['image'] = distribute_list
    single_images_list.append(single_dict)
    distributed_images_list.append(distribute_dict)
    img_list = []
    return single_images_list,distributed_images_list


def get_new_frame(line):
    name_list = line[0].split("_")
    new_line = []
    new_line.append(name_list[0])
    new_line.append(name_list[1])
    new_line.append(line[1])
    return new_line


def read_images_file(images_file_path):
    with open(images_file_path, "r+") as file:
        result_list = file.readlines()
    return result_list[0]


def get_frame():
    images_file_path = os.path.join(config_value("public_dir"), 'image_new_version.txt')
    ret_list = read_images_file(images_file_path)
    ret_list = eval(ret_list)
    single_list, distributed_list = regular_frame_and_version(ret_list)
    frame_version_list = {}
    frame_version_list["single_frame"] = single_list
    frame_version_list["distributed_frame"] = distributed_list
    return frame_version_list

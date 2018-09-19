# -*- coding:utf-8 -*-

import os
import sys
import argparse
import logging
import shutil
import traceback
import time
import logging

from PIL import Image
import gdal

from hyperai import log, utils
from hyperai.config import config_value
from hyperai.utils.image import open_tiff, trans_tiff_to_img
# from hyperai.utils.p_temp import get_op_info

logger = logging.getLogger('hyperai.tools.predict_images')

geo_ext = ['.tif', '.tiff']
attach_file_ext = ['.tif', '.tiff', '.tfw', '.tif.vat.dbf', '.tiff.vat.dbf', '.tif.aux.xml', '.tiff.aux.xml']


def just_tif(temp):
    if temp.endswith('tif'):
        return True
    return False


def save_to_png(im, tifpath, filename):
    pngname = '%s/%s.png' % (tifpath, os.path.splitext(filename)[0])
    im.save(pngname)
    return tifpath, pngname


def mk_folder(path):
    if os.path.exists(path):
        return True
    os.mkdir(path)


def transor(obj, **kwargs):
    i = 1
    for file_name in os.listdir(obj):
        if just_tif(os.path.splitext(file_name)[-1]):
            sys.stdout.flush()
            logger.info("Trans %s: [%s]" % (kwargs['image'], i))
            file_path = os.path.join(obj, file_name)
            feature_image = gdal.Open(file_path)
            save_images_path = os.path.join(kwargs['target_dir'], kwargs['image'])
            mk_folder(save_images_path)
            save_to_png(trans_tiff_to_img(feature_image), save_images_path, file_name)
            i += 1
    logger.info("Trans %s END." % kwargs['image'])
    return True


def main_func(args, **kwargs):
    job_dir = args['job_dir']
    task_flag = args['task_flag']
    feature_images = args['feature_images']
    label_images = args['label_images']
    num_threads = args['num_threads']
    target_dir = args['target_dir']
    mk_folder(target_dir)
    try:
        logger.info("----------  Feature images trans Start ----------")
        transor(feature_images, target_dir=target_dir, image="images")
        logger.info("----------  Label images trans Start ----------")
        transor(label_images, target_dir=target_dir, image="labels")
        return True
    except Exception as e:
        logger.error("predict images error: %s" % target_dir)
        return False


if __name__ == '__main__':
    parse = argparse.ArgumentParser()

    parse.add_argument('job_dir', help='job_dir.')
    parse.add_argument('target_dir', help='save images after transform.')
    parse.add_argument('-tf', '--task_flag', help=' ')
    parse.add_argument('-fi', '--feature_images', help='feature_images folder.')
    parse.add_argument('-li', '--label_images', help='label_images folder.')
    parse.add_argument('-nt', '--num_threads', help='The Count About Thread To EXEC Task.')

    args = vars(parse.parse_args())
    try:
        start_time = time.time()
        if main_func(args):
            time_total = time.time() - start_time
            sys.exit(0)
    except Exception as e:
        print e
        sys.exit(1)

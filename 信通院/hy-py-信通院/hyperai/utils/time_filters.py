#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-2017, NVIDIA CORPORATION.  All rights reserved.
from __future__ import absolute_import

import time



def print_time(t, ref_time=None):
    lt = time.localtime(t)

    # ref_time is for testing
    if ref_time is None:
        now = time.localtime()
    else:
        now = time.localtime(ref_time)

    if lt.tm_year != now.tm_year:
        return time.strftime('%b %d %Y, %I:%M:%S %p', lt).decode('utf-8')
    elif lt.tm_mon != now.tm_mon:
        return time.strftime('%b %d, %I:%M:%S %p', lt).decode('utf-8')
    elif lt.tm_mday != now.tm_mday:
        return time.strftime('%a %b %d, %I:%M:%S %p', lt).decode('utf-8')
    else:
        return time.strftime('%I:%M:%S %p', lt).decode('utf-8')


def print_time_diff(diff):
    if diff is None:
        return '?'

    if diff < 0:
        return 'Negative Time'

    total_seconds = int(diff)
    days = total_seconds // (24 * 3600)
    hours = (total_seconds % (24 * 3600)) // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    def plural(number, name):
        return '%d %s%s' % (number, name, '' if number == 1 else '')

    def pair(number1, name1, number2, name2):
        if number2 > 0:
            return '%s, %s' % (plural(number1, name1), plural(number2, name2))
        else:
            return '%s' % plural(number1, name1)

    if days >= 1:
        return pair(days, '天', hours, '小时')
    elif hours >= 1:
        return pair(hours, '小时', minutes, '分')
    elif minutes >= 1:
        return pair(minutes, '分', seconds, '秒')
    return plural(seconds, '秒')


def print_time_diff_nosuffixes(diff):
    if diff is None:
        return '?'

    hours, rem = divmod(diff, 3600)
    minutes, seconds = divmod(rem, 60)
    return '{:02d}:{:02d}:{:02d}'.format(int(hours), int(minutes), int(seconds))


def print_time_since(t):
    return print_time_diff(time.time() - t)


def transfer(old):
    if old == 'D':
        return u'完成'
    elif old == 1:
        return u'灰度图'
    elif old == 3:
        return u'彩色图'
    elif old == 'classification':
        return u'图像分类'
    elif old == 'E':
        return u'错误'
    elif old == 'R':
        return u'运行中'
    elif old == 'A':
        return u'终止'
    elif old == 'I':
        return '0%'
    elif old == 'W':
        return u'等待中'
    elif old == 'other':
        return u'其他'
    elif old == 'image-processing':
        return u'图像处理'
    elif old == 'image-segmentation':
        return u'图像分割'
    elif old == 'image-object-detection':
        return u'目标检测'
    elif old == 'text-classification':
        return '文本分类'
    elif old == 'image-sunnybrook':
        return '医疗影像'
    elif old == 'Raw Data':
        return '原始数据'
    elif old == 'Image output':
        return '图像输出'
    elif old == 'Bounding boxes':
        return '目标检测'
    elif old == 'Image Segmentation':
        return '图像分割'
    elif old == 'Text Classification':
        return '文本分类'
    elif old == 'Default':
        return '默认'
    elif old == 'Object Detection':
        return '目标检测'
    elif old == 'Processing':
        return '图像处理'
    elif old == 'Segmentation':
        return '图像分割'
    elif old == 'Classification':
        return '文本分类'
    elif old == 'Sunnybrook LV Segmentation':
        return '医疗影像 '






def get_count(tasks_list):
    b = 0
    for task in tasks_list:
        a = task.entries_count
        if a:
            b = b + a
    return b
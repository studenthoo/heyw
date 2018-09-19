#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-2017, NVIDIA CORPORATION.  All rights reserved.
from __future__ import absolute_import

import os
from influxdb import InfluxDBClient

influxdb_client = InfluxDBClient('172.22.32.75','8086','','','k8s')

try:
    sql = """select value from "cpu/usage_rate" where pod_name='ljf-20180628-033532-002d-785bd8554c-qv974' order by time desc limit 1"""
    print sql
    result = influxdb_client.query(sql)
    print list(result)
except Exception as e:
    print e

    import os


def eachfile(filepath):
    pathdir = os.listdir(filepath)
    for s in pathdir:
        newdir = os.path.join(filepath, s)  # 将文件名加入到当前文件路径后面
        if os.path.isfile(newdir):# 如果是文件
            if os.path.splitext(newdir)[1] == ".png":  # 如果文件是".png"后缀的
                print "222"
                # soundfile.append(newdir)
            elif os.path.isdir(newdir):  # 如果是路径
                eachfile(newdir)  # 递归
    return soundfile
fp = r'想要处理的文件的路径'
os.chdir(fp)
f = eachfile(fp)



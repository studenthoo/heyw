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


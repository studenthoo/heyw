# Copyright (c) 2014-2017, NVIDIA CORPORATION.  All rights reserved.
from __future__ import absolute_import

import os
import subprocess
import platform
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from hyperai.tools.deploy.kube import KubernetasCoord as k8s


def get_status():
    args = ['kubectl get po -n kube-system -o wide']
    output = k8s.short_exec_com(command=args)
    if output:
        pod_list = k8s.parse_pod_msg(element='monitoring-influxdb',content=output)
        if pod_list:
            ip = pod_list[0][-2]
            return ip


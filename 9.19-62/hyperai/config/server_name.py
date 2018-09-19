# Copyright (c) 2015-2017, NVIDIA CORPORATION.  All rights reserved.
from __future__ import absolute_import

import os
import platform

from . import option_list

if 'HYPERAI_SERVER_NAME' in os.environ:
    value = os.environ['HYPERAI_SERVER_NAME']
else:
    value = platform.node()

option_list['server_name'] = value

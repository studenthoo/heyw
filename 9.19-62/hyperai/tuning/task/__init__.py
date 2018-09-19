# Copyright (c) 2014-2017, NVIDIA CORPORATION.  All rights reserved.
from __future__ import absolute_import

from .train import ParaTrain
from hyperai.task import Task

__all__ = [
    'ParaTrain',
    'Task',
]

from hyperai.config import config_value
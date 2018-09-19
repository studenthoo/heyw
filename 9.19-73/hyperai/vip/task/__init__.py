# Copyright (c) 2014-2017, NVIDIA CORPORATION.  All rights reserved.
from __future__ import absolute_import

from .tensorflow_distributed import DistributedTrain
from .tensorflow_mpi import MpiDistributedTrain
from .caffe import CaffeTrain
from .caffe2 import DistributedCaffe2Train
from .torch import TorchTrain
from .mxnet import MxnetTrain
from .pytorch import PytorchTrain
from hyperai.task import Task
from .native_tensorflow import NativeDistributedTrain
# /root/hyperai/hyperai/task.py

__all__ = [
    'DistributedTrain',
    'MpiDistributedTrain',
    'CaffeTrain',
    'DistributedCaffe2Train',
    'TorchTrain',
    'PytorchTrain',
    'Task',
    'NativeDistributedTrain',
    'MxnetTrain',
]

from hyperai.config import config_value  # noqa




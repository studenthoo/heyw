# Copyright (c) 2014-2017, NVIDIA CORPORATION.  All rights reserved.
from __future__ import absolute_import

from .caffe_train import CaffeTrainTask
from .torch_train import TorchTrainTask
from .train import TrainTask

__all__ = [
    'CaffeTrainTask',
    'TorchTrainTask',
    'TrainTask',
]

from hyperai.config import config_value  # noqa

if config_value('tensorflow')['enabled']:
    from .tensorflow_train import TensorflowTrainTask  # noqa
    __all__.append('TensorflowTrainTask')
    from .tensorflow_train_mpi import TensorflowTrainTaskMpi  # noqa
    __all__.append('TensorflowTrainTaskMpi')


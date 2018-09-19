# Copyright (c) 2015-2017, NVIDIA CORPORATION.  All rights reserved.
from __future__ import absolute_import

# Create this object before importing the following imports, since they edit the list
option_list = {}

from .kuber_config import (yaml_dir, kubelog_dir)


def config_dir(option):
    """
    Return the current configuration value for the given option
    """
    return option_list[option]

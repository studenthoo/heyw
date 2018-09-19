# Copyright (c) 2015-2017, NVIDIA CORPORATION.  All rights reserved.
from __future__ import absolute_import

# Create this object before importing the following imports, since they edit the list
option_list = {}

from . import (  # noqa
    gpu_list,
    jobs_dir,
    log_file,
    server_name,
    store_option,
    url_prefix,
    generic,
)


def config_value(option):
    """
    Return the current configuration value for the given option
    """
    return option_list[option]

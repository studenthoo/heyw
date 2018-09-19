# Copyright (c) 2015-2017, NVIDIA CORPORATION.  All rights reserved.
from __future__ import absolute_import

import os
import tempfile

from . import option_list
import hyperai
import shutil


if 'HYPERAI_MODE_TEST' in os.environ:
    value = tempfile.mkdtemp()
elif 'HYPERAI_JOBS_DIR' in os.environ:
    value = os.environ['HYPERAI_JOBS_DIR']

else:
    raise IOError('Please set your /etc/profile HYPERAI_JOBS_DIR !')

value_public = os.path.join(value, 'public')
alljobs_dir = os.path.join(value, 'alljobs')

generate_yaml_dir = os.path.join(value_public, 'yaml_dir/generate_yamls')
template_yaml_dir = os.path.join(value_public, 'yaml_dir/templates')

try:
    value = os.path.abspath(value)
    if os.path.exists(value):
        if not os.path.isdir(value):
            raise IOError('No such directory: "%s"' % value)
        if not os.access(value, os.W_OK):
            raise IOError('Permission denied: "%s"' % value)
    if not os.path.exists(value):
        os.makedirs(value)
    if not os.path.exists(alljobs_dir):
        os.makedirs(alljobs_dir)
    if os.path.exists(value_public):
        if not os.path.isdir(value_public):
            raise IOError('No such directory: "%s"' % value)
        if not os.access(value_public, os.W_OK):
            raise IOError('Permission denied: "%s"' % value)
    if not os.path.exists(value_public):
        os.makedirs(value_public)
        # os.system('chmod -r 777 ' + value_public)
    if not os.path.exists(generate_yaml_dir):
        os.makedirs(generate_yaml_dir)
    if not os.path.exists(template_yaml_dir):
        os.makedirs(template_yaml_dir)

except:
    print '"%s" is not a valid value for jobs_dir.' % value
    print 'Set the envvar HYPERAI_JOBS_DIR to fix your configuration.'
    raise


option_list['jobs_dir'] = value
option_list['public_dir'] = value_public
option_list['alljobs_dir'] = alljobs_dir
option_list['generate_yaml_dir'] = generate_yaml_dir
option_list['template_yaml_dir'] = template_yaml_dir

generic_base_yaml = os.path.join(template_yaml_dir, 'base_job.yaml')
mpi_base_yaml = os.path.join(template_yaml_dir, 'mpi_base_job.yaml')
gpu_mpi_base_yaml = os.path.join(template_yaml_dir, 'gpu_mpi_base_job.yaml')

au_gpu_mpi_base_yaml = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                    'yaml_dir', 'au_gpu_mpi_base_job.yaml')
tensorrt_yaml = os.path.join(os.path.dirname(os.path.dirname(__file__)),'tools/deploy/template','tensorrt.yaml')
tfserving_yaml = os.path.join(os.path.dirname(os.path.dirname(__file__)),'tools/deploy/template','tfserving.yaml')
store_base_yaml_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'yaml_dir')
store_generic_base_yaml = os.path.join(store_base_yaml_dir, 'base_job.yaml')
store_mpi_base_yaml = os.path.join(store_base_yaml_dir, 'mpi_base_job.yaml')
store_gpu_mpi_base_yaml = os.path.join(store_base_yaml_dir, 'gpu_mpi_base_job.yaml')

if not os.path.exists(generic_base_yaml):
    try:
        shutil.copy(store_generic_base_yaml, generic_base_yaml)
    except Exception as e:
        raise
# else:
#     raise IOError('No such directory: "%s"' % generic_base_yaml)

if not os.path.exists(mpi_base_yaml):
    try:
        shutil.copy(store_mpi_base_yaml, mpi_base_yaml)
    except Exception as e:
        raise
# else:
#     raise IOError('No such directory: "%s"' % generic_base_yaml)

if not os.path.exists(gpu_mpi_base_yaml):
    try:
        shutil.copy(store_gpu_mpi_base_yaml, gpu_mpi_base_yaml)
    except Exception as e:
        raise
# else:
#     raise IOError('No such directory: "%s"' % generic_base_yaml)


gpu_mpi_base_yaml = store_gpu_mpi_base_yaml
mpi_base_yaml = store_mpi_base_yaml
generic_base_yaml = store_generic_base_yaml

option_list['generic_base_yaml'] = generic_base_yaml
option_list['mpi_base_yaml'] = mpi_base_yaml
option_list['gpu_mpi_base_yaml'] = gpu_mpi_base_yaml
option_list['au_gpu_mpi_base_yaml'] = au_gpu_mpi_base_yaml
option_list['tensorrt_yaml'] = tensorrt_yaml
option_list['tfserving_yaml'] = tfserving_yaml


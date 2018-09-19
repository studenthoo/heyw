# # -*- coding: utf-8 -*-
#
# import yaml
# import os
# import sys
# import shutil
#
# from . import option_list
#
#
# base_dir = os.environ['HYPERAI_JOBS_DIR']
# # publid_dir = option_list['public_dir']
# # generate_yaml_dir = os.path.join(publid_dir, 'yaml_dir/generate_yamls')
# # generate_yaml_dir = os.path.join(publid_dir, 'yaml_dir/generate_yamls')
#
# generate_yaml_dir = option_list['generate_yaml_dir']
# template_yaml_dir = option_list['template_yaml_dir']
#
# generic_base_yaml = os.path.join(template_yaml_dir, 'base_job.yaml')
# mpi_base_yaml = os.path.join(template_yaml_dir, 'mpi_base_job.yaml')
# gpu_mpi_base_yaml = os.path.join(template_yaml_dir, 'gpu_mpi_base_job.yaml')
#
# store_base_yaml_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'yaml')
# store_generic_base_yaml = os.path.join(store_base_yaml_dir, 'base_job.yaml')
# store_mpi_base_yaml = os.path.join(store_base_yaml_dir, 'mpi_base_job.yaml')
# store_gpu_mpi_base_yaml = os.path.join(store_base_yaml_dir, 'gpu_mpi_base_job.yaml')
# print("* " * 50)
# print('\n%s\n%s\n%s\n%s' % (store_base_yaml_dir,
#                             store_generic_base_yaml,
#                             store_mpi_base_yaml,
#                             store_gpu_mpi_base_yaml))
#
# if not os.path.exists(generic_base_yaml):
#     try:
#         shutil.copy(store_generic_base_yaml, generic_base_yaml)
#     except Exception as e:
#         raise
# else:
#     raise IOError('No such directory: "%s"' % generic_base_yaml)
#
# if not os.path.exists(mpi_base_yaml):
#     try:
#         shutil.copy(store_mpi_base_yaml, mpi_base_yaml)
#     except Exception as e:
#         raise
# else:
#     raise IOError('No such directory: "%s"' % generic_base_yaml)
#
# if not os.path.exists(gpu_mpi_base_yaml):
#     try:
#         shutil.copy(store_gpu_mpi_base_yaml, gpu_mpi_base_yaml)
#     except Exception as e:
#         raise
# else:
#     raise IOError('No such directory: "%s"' % generic_base_yaml)
#
# option_list['generic_base_yaml'] = generic_base_yaml
# option_list['mpi_base_yaml'] = mpi_base_yaml
# option_list['gpu_mpi_base_yaml'] = gpu_mpi_base_yaml

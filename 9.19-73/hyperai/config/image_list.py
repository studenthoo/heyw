import os
import sys
from . import option_list

image_list = {}

img_array = ['lwf_test_1802:lwf_test_0413_02',
             'hyperai_cloud:hyperai_cloud_v1.5',
             '10.18.101.85:80/hyperai/hyperai_cloud_v1.5:latest',
             'tem_hy:tem_hy_70']
             

mpi_image_array = ['lwf_test_1802:lwf_test_0413_02',
                   'hyperai_cloud:hyperai_cloud_v1.5',
                   '10.18.101.85:80/hyperai/hyperai_cloud_v1.5:latest',
                   'tem_hy:tem_hy_70'
                   ]


# image_list['mpi_image'] = mpi_image_array[2]
image_list['mpi_image'] = mpi_image_array[3]
# image_list['generic_image'] = img_array[2]
image_list['generic_image'] = img_array[3]

option_list['image_list'] = image_list


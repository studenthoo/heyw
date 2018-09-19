# Copyright (c) 2016-2017, NVIDIA CORPORATION.  All rights reserved.

import os
from setuptools import setup, find_packages

from hyperai.extensions.data import GROUP as HYPERAI_PLUGIN_GROUP


# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="hyperai_sunnybrook_data_plugin",
    version="0.0.1",
    author="Greg Heinrich",
    description=("A data ingestion plugin for the Sunnybrook cardiac dataset"),
    long_description=read('README'),
    license="Apache",
    packages=find_packages(),
    entry_points={
        HYPERAI_PLUGIN_GROUP: [
            'class=hyperaiDataPluginSunnybrook:DataIngestion',
        ]
    },
    include_package_data=True,
    install_requires=['pydicom'],
)

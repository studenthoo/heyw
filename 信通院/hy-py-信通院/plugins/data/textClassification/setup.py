import os
from setuptools import setup, find_packages
import sys
sys.path.append('/root/hyperai/hyperai/extensions/data')
print sys.path


# Copyright (c) 2016-2017, NVIDIA CORPORATION.  All rights reserved.
from hyperai.extensions.data import GROUP as HYPERAI_PLUGIN_GROUP


# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="hyperai_text_classification_data_plugin",
    version="0.0.1",
    author="Greg Heinrich",
    description=("A data ingestion plugin for text classification"),
    long_description=read('README'),
    license="BSD",
    packages=find_packages(),
    entry_points={
        HYPERAI_PLUGIN_GROUP: [
            'class=hyperaiDataPluginTextClassification:DataIngestion',
        ]},
    include_package_data=True,
)

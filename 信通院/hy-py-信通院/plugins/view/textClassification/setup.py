import os
from setuptools import setup, find_packages

# Copyright (c) 2016-2017, NVIDIA CORPORATION.  All rights reserved.
from hyperai.extensions.view import GROUP as HYPERAI_PLUGIN_GROUP


# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="hyperai_text_classification_view_plugin",
    version="0.0.1",
    author="Greg Heinrich",
    description=("A view plugin for text classification"),
    long_description=read('README'),
    license="BSD",
    packages=find_packages(),
    entry_points={
        HYPERAI_PLUGIN_GROUP: [
            'class=hyperaiViewPluginTextClassification:Visualization',
        ]},
    include_package_data=True,
)

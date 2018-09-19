# coding: utf-8


from __future__ import absolute_import

import os
import sys
import re

import hyperai
from hyperai import utils
from hyperai.config import config_value
from hyperai.task import Task
from hyperai.utils import subclass, override


PICKLE_VERSION = 1

@subclass
class ExtractDatasetTask(Task):

    def __init__(self, target_dir, feature_images_path, label_images_path, num_threads, **kwargs):

        self.feature_images = feature_images_path
        self.label_images = label_images_path

        super(ExtractDatasetTask, self).__init__(**kwargs)
        self.pickver_task_extract_dataset = PICKLE_VERSION
        self.entry_count = 0
        self.stage = None
        self.dbs = None
        self.num_threads = num_threads
        self.target_dir = target_dir

        self.flag = "extra-ds-task"

    @override
    def name(self):
        return 'Extract dataset file'


    @override
    def html_id(self):
        return 'extract-dataset-file-%s' % os.path.splitext(os.path.basename(self.target_dir))[0]


    @override
    def offer_resources(self, resources, locking_gpu=False):
        key = 'extract_dataset_file_pool'
        if key not in resources:
            return None
        for resource in resources[key]:
            if resource.remaining() >= 1:
                return {key: [(resource.identifier, 1)]}
        return None


    @override
    def task_arguments(self, resources, env):
        args = [sys.executable,
                os.path.join(os.path.dirname(os.path.abspath(hyperai.__file__)), 'tools', 'predict_images.py'),
                self.job_dir,
                self.target_dir,
                '--task_flag=%s' % self.flag,
                '--feature_images=%s' % self.feature_images,
                '--label_images=%s' % self.label_images,
                '--num_threads=%s' % self.num_threads,
                ]

        resources_args = {}

        return args, resources_args


    @override
    def process_output(self, line):
        _, level, message = self.preprocess_output_hyperai(line)
        if not message:
            return False

        # progress
        match = re.match(r'Progress: ([-+]?[0-9]*\.?[0-9]+(e[-+]?[0-9]+)?)', message)
        if match:
            self.progress = float(match.group(1))
            self.emit_progress_update()
            return True

        if level == 'warning':
            self.logger.warning('%s: %s' % (self.name(), message))
        elif level == 'info':
            self.logger.info('%s: %s' % (self.name(), message))
        elif level in ['error', 'critical']:
            self.logger.error('%s: %s' % (self.name(), message))
            self.exception = message

        return True



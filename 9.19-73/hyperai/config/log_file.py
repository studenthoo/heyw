# Copyright (c) 2015-2017, NVIDIA CORPORATION.  All rights reserved.
from __future__ import absolute_import

import logging
import os

from . import option_list
import hyperai


def load_logfile_filename():
    """
    Return the configured log file or None
    Throws an exception only if a manually specified log file is invalid
    """
    throw_error = False
    if 'HYPERAI_MODE_TEST' in os.environ:
        filename = None
    elif 'HYPERAI_LOGFILE_FILENAME' in os.environ:
        filename = os.environ['HYPERAI_LOGFILE_FILENAME']
        throw_error = True
    else:
        filename = os.path.join(os.path.dirname(hyperai.__file__), 'hyperai.log')

    if filename is not None:
        try:
            filename = os.path.abspath(filename)
            dirname = os.path.dirname(filename)
            if not os.path.exists(dirname):
                os.makedirs(os.path.dirname(filename))
            with open(filename, 'a'):
                pass
        except:
            if throw_error:
                print '"%s" is not a valid value for logfile_filename.' % filename
                print 'Set the envvar HYPERAI_LOGFILE_FILENAME to fix your configuration.'
                raise
            else:
                filename = None
    return filename


def load_logfile_level():
    """
    Return the configured logging level, or throw an exception
    """
    if 'HYPERAI_MODE_TEST' in os.environ:
        return logging.DEBUG
    elif 'HYPERAI_LOGFILE_LEVEL' in os.environ:
        level = os.environ['HYPERAI_LOGFILE_LEVEL'].strip().lower()
        if level == 'debug':
            return logging.DEBUG
        elif level == 'info':
            return logging.INFO
        elif level == 'warning':
            return logging.WARNING
        elif level == 'error':
            return logging.ERROR
        elif level == 'critical':
            return logging.CRITICAL
        else:
            raise ValueError(
                'Invalid value "%s" for logfile_level. '
                'Set HYPERAI_LOGFILE_LEVEL to fix your configuration.' % level)
    else:
        return logging.INFO


option_list['log_file'] = {
    'filename': load_logfile_filename(),
    'level': load_logfile_level(),
}

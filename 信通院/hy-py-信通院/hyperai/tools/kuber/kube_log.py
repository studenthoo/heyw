# Copyright (c) 2014-2017, NVIDIA CORPORATION.  All rights reserved.
from __future__ import absolute_import

import logging
import logging.handlers
import sys
import os

from hyperai.tools.kuber import config_dir


DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


class JobIdLogger(logging.Logger):

    def makeRecord(self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None):
        """
        Customizing it to set a default value for extra['job_id']
        """
        rv = logging.LogRecord(name, level, fn, lno, msg, args, exc_info, func)
        if extra is not None:
            for key in extra:
                if (key in ["message", "asctime"]) or (key in rv.__dict__):
                    raise KeyError("Attempt to overwrite %r in LogRecord" % key)
                rv.__dict__[key] = extra[key]
        if 'job_id' not in rv.__dict__:
            rv.__dict__['job_id'] = ''
        return rv


class JobIdLoggerAdapter(logging.LoggerAdapter):
    """
    Accepts an optional keyword argument: 'job_id'

    You can use this in 2 ways:
        1. On class initialization
            adapter = JobIdLoggerAdapter(logger, {'job_id': job_id})
            adapter.debug(msg)
        2. On method invocation
            adapter = JobIdLoggerAdapter(logger, {})
            adapter.debug(msg, job_id=id)
    """

    def process(self, msg, kwargs):
        if 'job_id' in kwargs:
            if 'extra' not in kwargs:
                kwargs['extra'] = {}
            kwargs['extra']['job_id'] = ' [%s]' % kwargs['job_id']
            del kwargs['job_id']
        elif 'job_id' in self.extra:
            if 'extra' not in kwargs:
                kwargs['extra'] = {}
            kwargs['extra']['job_id'] = ' [%s]' % self.extra['job_id']
        return msg, kwargs


def setup_logging(flag,job_id):
    # Set custom logger
    logging.setLoggerClass(JobIdLogger)
    formatter = logging.Formatter(
        fmt="%(asctime)s%(job_id)s [%(levelname)-5s] %(message)s",
        datefmt=DATE_FORMAT,
    )

    # sh_logger = logging.getLogger('kube_stream')
    # sh_logger.setLevel(logging.DEBUG)
    #
    # sh = logging.StreamHandler(sys.stdout)
    # sh.setFormatter(formatter)
    # sh.setLevel(logging.DEBUG)
    # sh_logger.addHandler(sh)

    kubelog_dir = config_dir('kubelog_dir')
    log_name = str(flag)+"-"+ str(job_id) + ".log"
    kubelog_path = os.path.join(kubelog_dir, log_name)

    if kubelog_path is not None:
        file_logger = logging.getLogger('kube_file')
        file_logger.setLevel(logging.DEBUG)

        fh = logging.FileHandler(kubelog_path, "w")
        fh.setFormatter(formatter)
        fh.setLevel(logging.DEBUG)
        file_logger.addHandler(fh)

        # Useful shortcut for the webapp, which may set job_id

        return JobIdLoggerAdapter(file_logger,{'job_id':job_id})
    else:
        print 'WARNING: log_file config option not found - no log file is being saved'
        return JobIdLoggerAdapter(sh_logger, {'job_id':job_id})

# Do it when this module is loaded
# setup_logging(flag,job_id)


# set_logger(self):
#     logger = hyperai.log.JobIdLoggerAdapter(
#         logging.getLogger('hyperai.webapp'),
#         {'job_id':job_id},
#     )









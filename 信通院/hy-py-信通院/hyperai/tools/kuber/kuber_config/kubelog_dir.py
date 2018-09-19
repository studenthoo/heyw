# Copyright (c) 2015-2017, NVIDIA CORPORATION.  All rights reserved.
from __future__ import absolute_import

import os
import tempfile

from hyperai.tools.kuber import option_list
import hyperai


if 'HYPERAI_MODE_TEST' in os.environ:
    value = tempfile.mkdtemp()
elif 'HYPERAI_KUBELOG_DIR' in os.environ:
    value = os.environ['HYPERAI_KUBELOG_DIR']
else:
    # value = os.path.join(os.path.dirname(hyperai.__file__), 'jobs')
    value = os.path.join('/home/nfsdir', 'public')

value = os.path.join(value, "kubelog_dir")

try:
    value = os.path.abspath(value)
    if os.path.exists(value):
        if not os.path.isdir(value):
            raise IOError('No such directory: "%s"' % value)
        if not os.access(value, os.W_OK):
            raise IOError('Permission denied: "%s"' % value)
    if not os.path.exists(value):
        os.makedirs(value)
except:
    print '"%s" is not a valid value for kubelog_dir.' % value
    print 'Set the envvar HYPERAI_KUBELOG_DIR to fix your configuration.'
    raise


option_list['kubelog_dir'] = value

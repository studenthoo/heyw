# Copyright (c) 2014-2017, NVIDIA CORPORATION.  All rights reserved.
from __future__ import absolute_import

from flask.ext.wtf import Form
from wtforms.validators import DataRequired

from hyperai import utils


class DatasetForm(Form):
    """
    Defines the form used to create a new Dataset
    (abstract class)
    """

    dataset_name = utils.forms.StringField(u'Dataset Name',
                                           )
    dataset_desc = utils.forms.StringField(u'Dataset desc',
                                           )
    group_name = utils.forms.StringField('Group Name',
                                         tooltip="An optional group name for organization on the main page."
                                         )
    dataset_name_text = utils.forms.StringField(u'Dataset Name',

                                           )
    dataset_desc_text = utils.forms.StringField(u'Dataset desc',
                                           )
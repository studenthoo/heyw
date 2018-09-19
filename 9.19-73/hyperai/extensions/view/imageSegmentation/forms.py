#coding=utf-8
from __future__ import absolute_import

from flask.ext.wtf import Form

from hyperai import utils
from hyperai.utils import subclass


@subclass
class ConfigForm(Form):
    """
    A form used to display the network output as an image
    """
    colormap = utils.forms.SelectField(
        #'Colormap',
        u'彩图',
        choices=[
            ('dataset', 'From dataset'),
            ('paired', 'Paired (matplotlib)'),
            ('none', 'None (grayscale)'),
        ],
        default='dataset',
        tooltip='Set color map to use when displaying segmented image'
    )

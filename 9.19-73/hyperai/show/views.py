from __future__ import absolute_import

from flask import Blueprint, request, render_template, g, session

from hyperai.utils.auth import requires_login
from hyperai.models import User
from hyperai.utils.auth import requires_login

blueprint = Blueprint(__name__, __name__)








@blueprint.route('/model/forecast')
@requires_login
def model_forecast_new():
    return render_template('/new/model-Forecast.html',index='forecast')


@blueprint.route('/model/shop/<path>')
@requires_login
def shop(path):
    return render_template('/new/shareShop-ModelDataShop.html', index='shop',path=path)





@blueprint.route('/shop/dataset')
@requires_login
def shop_dataset():

    return render_template('/new/shareShop-DataDetails.html')


@blueprint.route('/shop/model')
@requires_login
def shop_model():

    return render_template('/new/shareShop-ModelDetails.html')
from __future__ import absolute_import

from flask import Blueprint, request, render_template, g, session
import flask
from hyperai.utils.auth import requires_login
from hyperai.models import User
from hyperai.utils.auth import requires_login

blueprint = Blueprint(__name__, __name__)


@blueprint.route('/advance', methods=['GET'])
@requires_login
def advance():
    return flask.render_template('new/Vipuser.html')

@requires_login
@blueprint.route('/advance/monitor', methods=['GET', 'POST'])
def advance_monitor():
    return flask.render_template('/new/v-homeworkMonitor.html')


@requires_login
@blueprint.route('/paraopt', methods=['GET', 'POST'])
def para_opt():
    return flask.render_template('new/tuning.html')


@requires_login
@blueprint.route('/paraopt/monitor', methods=['GET', 'POST'])
def para_opt_monitor():
    return flask.render_template('/new/tuning-result.html')
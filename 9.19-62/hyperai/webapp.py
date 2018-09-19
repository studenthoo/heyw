# Copyright (c) 2014-2017, NVIDIA CORPORATION.  All rights reserved.
from __future__ import absolute_import
import sys
reload(sys)
sys.setdefaultencoding('utf8') 
import os

import flask
from flask.ext.socketio import SocketIO
from gevent import monkey

monkey.patch_all()
from .ext import db, create_app, r
from .config import config_value  # noqa
from hyperai import utils  # noqa
from hyperai.utils import filesystem as fs  # noqa
from hyperai.utils.store import StoreCache  # noqa
import hyperai.scheduler  # noqa

# Create Flask, Scheduler and SocketIO objects

url_prefix = config_value('url_prefix')
# app = flask.Flask(__name__, static_url_path=url_prefix + '/static')
app = create_app('development', url_prefix)

app.config['DEBUG'] = True
db.init_app(app)
# Disable CSRF checking in WTForms
app.config['WTF_CSRF_ENABLED'] = False
# This is still necessary for SocketIO
app.config['SECRET_KEY'] = os.urandom(12).encode('hex')
app.url_map.redirect_defaults = False
app.config['URL_PREFIX'] = url_prefix
socketio = SocketIO(app, async_mode='gevent', path=url_prefix + '/socket.io')
app.config['store_cache'] = StoreCache()
app.config['store_url_list'] = config_value('model_store')['url_list']
# scheduler = hyperai.scheduler.Scheduler(config_value('gpu_list'), True)
scheduler = hyperai.scheduler.Scheduler(config_value('gpu_list'))

# Register filters and views

app.jinja_env.globals['server_name'] = config_value('server_name')
app.jinja_env.globals['server_version'] = hyperai.__version__
# app.jinja_env.globals['caffe_version'] = config_value('caffe')['version']
# app.jinja_env.globals['caffe_flavor'] = config_value('caffe')['flavor']
app.jinja_env.globals['dir_hash'] = fs.dir_hash(
    os.path.join(os.path.dirname(hyperai.__file__), 'static'))
app.jinja_env.globals['jupyter_ip'] = config_value('jupyter_ip')
app.jinja_env.globals['jupyter_port'] = config_value('jupyter_port')
app.jinja_env.globals['grafana_ip'] = config_value('grafana_ip')
app.jinja_env.globals['grafana_port'] = config_value('grafana_port')
app.jinja_env.globals['deploy_ip'] = config_value('deploy_ip')
app.jinja_env.globals['hyperai_ip'] = config_value('hyperai_ip')
app.jinja_env.globals['hyperai_port'] = config_value('hyperai_port')
app.jinja_env.filters['print_time'] = utils.time_filters.print_time
app.jinja_env.filters['print_time_diff'] = utils.time_filters.print_time_diff
app.jinja_env.filters['print_time_since'] = utils.time_filters.print_time_since
app.jinja_env.filters['sizeof_fmt'] = utils.sizeof_fmt
app.jinja_env.filters['has_permission'] = utils.auth.has_permission
app.jinja_env.filters['transfer'] = utils.time_filters.transfer
app.jinja_env.filters['get_count'] = utils.time_filters.get_count
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

import hyperai.views  # noqa

app.register_blueprint(hyperai.views.blueprint,url_prefix=url_prefix)


import hyperai.passport.views  # noqa

app.register_blueprint(
    hyperai.passport.views.blueprint, url_prefix=url_prefix + '/user'
)


import hyperai.vip.views  # noqa

app.register_blueprint(hyperai.vip.views.blueprint,
                       url_prefix=url_prefix + '/vip')

import hyperai.tuning.views  # noqa

app.register_blueprint(hyperai.tuning.views.blueprint,
                       url_prefix=url_prefix + '/tuning')


import hyperai.sysmanager.views  # noqa

app.register_blueprint(hyperai.sysmanager.views.blueprint,
                       url_prefix=url_prefix + '/sysmanager')

import hyperai.show.views  # noqa
app.register_blueprint(
    hyperai.show.views.blueprint, url_prefix=url_prefix+'/show'
)

def username_decorator(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        this_username = flask.request.cookies.get('username', None)
        app.jinja_env.globals['username'] = this_username
        return f(*args, **kwargs)

    return decorated


for endpoint, function in app.view_functions.iteritems():
    app.view_functions[endpoint] = username_decorator(function)

# Setup the environment
print 1234567890
r.flushdb()
print "Reset the Redis."
scheduler.set_user_gpu()
scheduler.load_past_jobs_scheduler()

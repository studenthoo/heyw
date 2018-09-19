from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from database import config
# import redis
import os
from influxdb import InfluxDBClient
# from hyperai.config import config_value

db = SQLAlchemy()

jobs = os.environ.get('HYPERAI_ROOT')
if jobs is None:
    print "Not Found ENV HYPERAI_ROOT."
    print "Set The jobs: /root/hyperai"
    jobs = '/root/hyperai'
config_path = os.path.join(jobs, 'Hyperai.config')

def open_config_f():
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            lists = f.readlines()
            return lists
    else:
        raise IOError('config file {} not found!'.format(config_path))



contents = open_config_f()
for line in contents:
    line = line.strip()
    if line.startswith('mysql_ip') and line.endswith('='):
        mysql_ip = '127.0.0.1'
    elif line.startswith('mysql_ip') and not line.endswith('='):
        mysql_ip = line.split('=')[-1].strip()
    if line.startswith('mysql_port') and line.endswith('='):
        mysql_port = '3306'
    elif line.startswith('mysql_port') and not line.endswith('='):
        mysql_port = line.split('=')[-1].strip()
    if line.startswith('mysql_db') and line.endswith('='):
        mysql_db = 'test'
    elif line.startswith('mysql_db') and not line.endswith('='):
        mysql_db = line.split('=')[-1].strip()
    if line.startswith('mysql_user') and line.endswith('='):
        mysql_user = 'root'
    elif line.startswith('mysql_user') and not line.endswith('='):
        mysql_user = line.split('=')[-1].strip()
    if line.startswith('mysql_password') and line.endswith('='):
        mysql_password = '123456'
    elif line.startswith('mysql_password') and not line.endswith('='):
        mysql_password = line.split('=')[-1].strip()
    if line.startswith('redis_ip') and line.endswith('='):
        redis_ip = 'localhost'
    elif line.startswith('redis_ip') and not line.endswith('='):
        redis_ip = line.split('=')[-1].strip()
    if line.startswith('redis_port') and line.endswith('='):
        redis_port = '6379'
    elif line.startswith('redis_port') and not line.endswith('='):
        redis_port = line.split('=')[-1].strip()
    if line.startswith('redis_db') and line.endswith('='):
        redis_db = 0
    elif line.startswith('redis_db') and not line.endswith('='):
        redis_db = line.split('=')[-1].strip()


class Config:
    SQLACHEMY_COMMIT_ON_TEARDOWN = True

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://{}:{}@{}:{}/{}'.format(mysql_user,mysql_password,mysql_ip,mysql_port,mysql_db)
    # print SQLALCHEMY_DATABASE_URI,'----->'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# class TestingConfig(Config):
#     DEBUG = True
#     SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@127.0.0.1:3306/test'
#     SQLALCHEMY_TRACK_MODIFICATIONS = False


config = {
    'development': DevelopmentConfig,
}

def create_app(config_name, url=None):
    if url is not None:
        app = Flask(__name__, static_url_path=url + '/static')
    else:
        app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    return app


# r = redis.Redis(host=config_value('redis_ip'), port = config_value('redis_port'), db = config_value('redis_db'))
# r = redis.Redis(host=redis_ip, port = redis_port, db = redis_db)


if 'ip' in os.environ:
    # print 1111111
    ip = os.environ['ip']
    influxdb_client = InfluxDBClient(ip,'8086','','','k8s')

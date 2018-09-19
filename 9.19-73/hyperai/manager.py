# coding=utf-8

from flask_migrate import Migrate, MigrateCommand
from flask_script import Shell, Manager
from ext import db, create_app
import models

app = create_app('development')

db.init_app(app)

# 第一个参数是Flask的实例，第二个参数是Sqlalchemy数据库实例
Migrate(app, db)
manager = Manager(app)

# manager是Flask-Script的实例，这条语句在flask-Script中添加一个db命令
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()

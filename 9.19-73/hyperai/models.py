# coding=utf-8

from datetime import datetime

from ext import db

user_to_dataset = db.Table('user_to_dataset',
                           db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                           db.Column('dataset_id', db.Integer, db.ForeignKey('datasets.id')))

user_to_model = db.Table('user_to_model',
                         db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                         db.Column('model_id', db.Integer, db.ForeignKey('models.id')))
user_to_department = db.Table('user_to_department',
                         db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                         db.Column('department_id', db.Integer, db.ForeignKey('departments.id')))

class BaseModel(object):
    """模型基类，为每个模型补充创建时间和更新时间"""
    create_time = db.Column(db.DateTime, default=datetime.now)  # 记录创建的时间
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 记录的更新时间


class User(BaseModel, db.Model):
    """用户表"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)  # 用户编号
    name = db.Column(db.String(32), unique=True, nullable=False)  # 用户名   不能为空
    password = db.Column(db.String(128), nullable=False)  # 加密的密码
    # department = db.Column(db.String(64), nullable=False)  # 用户所属部门
    real_name = db.Column(db.String(32), nullable=False)  # 用户真实姓名
    phone = db.Column(db.String(11), nullable=False)  # 用户电话
    email = db.Column(db.String(128), nullable=False)  # 邮箱
    permission = db.Column(db.String(20))  # 用户资源分配权限
    integral = db.Column(db.Integer, default=10000)  # 用户积分
    gpu_used = db.Column(db.Integer, default=0)
    examined = db.Column(db.Boolean, default=False)
    release = db.Column(db.Boolean, default=False)
    # model = db.relationship('Model', backhref='user')

    def __repr__(self):
        return 'user:{}'.format(self.name)

    @staticmethod
    def get_depart(username):
        user = User.query.filter_by(name=username).first()
        depart = user.departments.first()

        if depart:
            return depart.depart_power
        else:
            return None

    @staticmethod
    def get_gpu_max(username):
        user = User.query.filter_by(name=username).first()
        depart = user.departments.first()

        # print "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", depart
        if depart:
            return depart.gpu_max
        else:
            return 0

    def to_dict(self):
        """将对象转化为字典"""
        user_dict = {
            "user_id": self.id,
            "name": self.name,
            "department": self.department,
            "phone": self.phone,
        }
        return user_dict


class Dataset(BaseModel, db.Model):
    """数据集"""
    __tablename__ = 'datasets'

    id = db.Column(db.Integer, primary_key=True)  # 主键id
    publish_user = db.Column(db.String(32), nullable=False)  # 发布者
    name = db.Column(db.String(64), nullable=False)  # 数据集名称
    apply_scenes = db.Column(db.String(64), nullable=False)  # 应用场景
    data_num = db.Column(db.String(20), nullable=False)  # 数据个数
    buy_num = db.Column(db.Integer, default=0)  # 购买次数
    desc = db.Column(db.String(256), nullable=False)  # 描述
    data_type = db.Column(db.String(12), nullable=False)  # 数据类型
    permissions = db.Column(
        db.Enum(
            'U',  # 用户私有
            'D',  # 部门内可见
            'S'  # 商店　所有人可见
        ),
        default='U', index=True  # 建立索引
    )
    department = db.Column(db.String(24), nullable=True)  # 部门 可以为空
    # star = db.Column(db.Float, default=0)  # 数据集评分 默认为零 后续需要计算评论评分平均值
    dataset_path = db.Column(db.String(256), nullable=False)  # 数据集文件路径
    job_id = db.Column(db.String(64))  # dataset_job_id
    comment = db.relationship("Comment")  # 外键  评论表
    pic_path = db.Column(db.String(256))
    # price = db.Column(db.Integer)
    dataset = db.relationship('User', secondary=user_to_dataset, backref=db.backref('datasets', lazy='dynamic'),
                              lazy='dynamic')

    def __repr__(self):
        return 'Dataset:{}'.format(self.name)

    def to_basic_dict(self):
        dataset_dict = {
            "id": self.id,
            "publish_user": self.publish_user,
            "name": self.name,
            # "star": self.star,
            "create_time": self.create_time.strftime('%Y-%m-%d'),
            "desc": self.desc,
            "job_id": self.job_id
        }
        return dataset_dict

    def to_full_dict(self):
        # 数据集详细信息
        dataset_dict = {
            "id": self.id,
            "publish_user": self.publish_user,
            "name": self.name,
            # "star": self.star,
            "create_time": self.create_time.strftime('%Y-%m-%d'),
            "desc": self.desc,
            "apply_scenes": self.apply_scenes,
            "data_num": self.data_num,
            "data_type": self.data_type,
            "data_path": self.dataset_path,
            # "department": self.department,
            "permission": self.permissions,
            "pic_path": self.pic_path,
            "job_id": self.job_id,
            "buy_num": self.buy_num,
        }
        return dataset_dict


class Model(BaseModel, db.Model):
    __tablename__ = 'models'

    id = db.Column(db.Integer, primary_key=True)  # 主键id
    publish_user = db.Column(db.String(32), nullable=False)  # 发布者
    name = db.Column(db.String(64), nullable=False)  # 模型名称
    apply_scenes = db.Column(db.String(256), nullable=False)  # 应用场景
    framework = db.Column(db.String(20), nullable=False)  # 训练框架
    network = db.Column(db.String(20), nullable=False)  # 网络
    accuracy = db.Column(db.String(10), nullable=False)  # 准确率
    buy_num = db.Column(db.Integer, default=0)  # 购买次数
    desc = db.Column(db.String(256), nullable=False)  # 模型描述
    model_path = db.Column(db.String(256), nullable=False)  # 模型文件路径
    permissions = db.Column(
        db.Enum(
            'U',  # 用户私有
            'D',  # 部门内可见
            'S'  # 商店　所有人可见
        ),
        default='U', index=True  # 建立索引
    )
    department = db.Column(db.String(24), nullable=True)  # 部门 可以为空
    # star = db.Column(db.Float, default=0)  # 模型评分 默认为零 后续需要计算评论评分平均值
    job_id = db.Column(db.String(64))  # model_job_id
    comment = db.relationship("Comment")  # 评论表
    # price = db.Column(db.Integer)
    models = db.relationship('User', secondary=user_to_model, backref=db.backref('models', lazy='dynamic'),
                             lazy='dynamic')

    def __repr__(self):
        return 'Model:{}'.format(self.name)

    def to_basic_dict(self):
        # 模型基础信息
        model_dict = {
            "id": self.id,
            "publish_user": self.publish_user,
            "name": self.name,
            # "star": self.star,
            "create_time": self.create_time.strftime('%Y-%m-%d'),
            "desc": self.desc,
            "job_id": self.job_id
        }
        return model_dict

    def to_full_dict(self):
        # 模型详细信息
        model_dict = {
            "id": self.id,
            "publish_user": self.publish_user,
            "name": self.name,
            # "star": self.star,
            "create_time": self.create_time.strftime('%Y-%m-%d'),
            "desc": self.desc,
            "framework": self.framework,
            "accuracy": self.accuracy,
            "network": self.network,
            "apply_scenes": self.apply_scenes,
            # "department": self.department,
            "permission": self.permissions,
            "job_id": self.job_id,
            "buy_num":self.buy_num,
        }
        return model_dict


class Comment(BaseModel, db.Model):
    """评论表"""

    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)  # 评论id  主键
    comment_name = db.Column(db.String(32), nullable=False)  # 评论者名字
    comment_content = db.Column(db.Text, nullable=False)  # 评论内容
    # comment_star = db.Column(db.Float, nullable=False)  # 评分等级
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'))
    model_id = db.Column(db.Integer, db.ForeignKey('models.id'))

    def __repr__(self):
        return 'Comment:{}'.format(self.comment_name)

    def to_dict(self):
        comment_dict = {
            "id": self.id,
            "comment_name": self.comment_name,
            # "comment_star": self.comment_star,
            "comment_content": self.comment_content,
            "time":self.create_time.strftime('%Y-%m-%d'),
        }
        return comment_dict


class Department(BaseModel,db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    depart_name = db.Column(db.String(256))
    depart_power = db.Column(db.Integer)
    departments = db.relationship('User', secondary=user_to_department, backref=db.backref('departments', lazy='dynamic'),
                         lazy='dynamic')
    gpu_max = db.Column(db.Integer)

    def __repr__(self):
        return 'depart_name:{}'.format(self.depart_name)

class Monitor(BaseModel, db.Model):
    _tablename_ = 'monitor'

    id = db.Column(db.Integer, primary_key=True)  # 主键
    gpu_utilization = db.Column(db.String(256))
    pod_name = db.Column(db.String(256))
    memory = db.Column(db.String(256))

# class Pretrained_network(BaseModel, db.Model):
#     """之前使用过的神经网络表"""
#     __tablename__ = 'networks'
#     id = db.Column(db.Integer, primary_key=True)
#     job_id = db.Column(db.String(64))  # pretrained_model的job_id
#     path = db.Column(db.String(256))
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
#
#     def to_dict(self):
#         network_dict = {
#             'id': self.id,
#             'job_id': self.job_id,
#             'path': self.path,
#             'user_id': self.user_id if self.user_id else ""
#         }
#         return network_dict
#
#
# class Student(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(24))
#
#     def __repr__(self):
#         return self.name
#

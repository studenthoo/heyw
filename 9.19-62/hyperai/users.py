# !/usr/bin/python
# -*- coding:utf-8 -*-
from io import StringIO
from hyperai.models import User

class RegisterUsers(object):
    """"""
    def __init__(self):
        self.user_dict = {}
        pass

    def allocate_resources(self, username, task_obj):
        if username not in self.user_dict:
            self.user_dict[username] = []
        for task in self.user_dict[username]:
            if id(task) == id(task_obj):
                # print "The same task prohibits multiple deductions."
                task_obj.logger.info("Allocate GPU Failed about user. %s" % username)
                return False
        self.user_dict[username].append(task_obj)
        print([(i.gpu_count, i.node_count) for i in self.user_dict[username]])
        task_obj.logger.info("Allocate GPU: <{username}> - {num}".format(username=username,
                                                                         num=task_obj.gpu_count * task_obj.node_count))
        task_obj.logger.info("该用户 {username} 已使用GPU: {num}\n".format(username=username,
                                                                             num=self.get_used_resource_about_user(
                                                                                 username)))
        return True

    def deallocate_resources(self, username, task_obj):
        print "释放资源。。。。"
        if username not in self.user_dict:
            task_obj.logger.error("Not found user: %s" % username)
            # print("Not found user: %s" % username)
            return False
        if not self.user_dict[username]:
            print("Not found any resources about user: %s" % username)
        for i, task in enumerate(self.user_dict[username]):
            if id(task) == id(task_obj):
                self.user_dict[username].pop(i)
                task_obj.logger.info("Release GPU: <{username}> - {num}".format(username=username,
                                                                                num=task_obj.gpu_count * task_obj.node_count))
                task_obj.logger.info("该用户 {username} 已使用GPU: {num}\n".format(username=username,
                                                                                num=self.get_used_resource_about_user(username)))
                return True
        task_obj.logger.error("Release GPU Failed about user. %s" % username)
        raise RuntimeError("Release GPU Failed about user.")
        # return False

    def get_resource_about_user(self, username):
        pass

    def get_used_resource_about_user(self, username):
        """
        如果没有用户的记录，说明该用户已用资源为0，
        返回指定用户已用的GPU
        """
        if username not in self.user_dict:
            # print "没有发现该用户：", username
            return 0
        if username in self.user_dict:
            num = 0
            for task in self.user_dict[username]:
                num += int(task.gpu_count) * int(task.node_count)
            # print("*******", num)
            return num

    def is_enough_resource_about_user(self, username, value, max_value):
        """"""
        user = User.query.filter_by(name=username).first()
        if user.release:
            return 'Forbid'
        # if username in self.user_dict:
        #     print(username, "*****", [(i.job.id(), i.gpu_count) for i in self.user_dict[username]])
        used_num = self.get_used_resource_about_user(username)
        if value > max_value - used_num:
            return False
        return True


register_user = RegisterUsers()

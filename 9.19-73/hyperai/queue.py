# -*- coding:utf-8 -*-


class PriorityQueue(object):
    def __init__(self):
        self._queue = []

    def __str__(self):
        return "the queue is : {} ,the queue len is: {}".format([x for x in self._queue], self.length())

    def put(self, job):
        """temp: a job object"""
        # TODO 是否可能存在同时添加多个job，需要改进
        if self.is_empty():
            self._queue.append(job)
        else:
            num = self.length()
            while num >= 0:
                if num == 0:
                    self._queue.insert(0, job)
                    break
                # if job[1] > self._queue[num-1][1]:
                if job.pri() > self._queue[num-1].pri():
                    self._queue.insert(num, job)
                    break
                else:
                    num -= 1

    def get_by_index(self, index=-1):
        # 根据给定的索引值获取对应的job,默认获取队列内最后一个
        if not self.is_empty() and index < self.length():
            return self._queue[index]
        return None
        pass

    def pop_by_index(self, index=-1):
        # pop指定索引元素，默认为队列的最后一个
        if not self.is_empty() and index < self.length():
            return self._queue.pop(index)
        return None
        pass

    def remove_by_job_id(self, job_id):
        if job_id:
            for job in self._queue:
                if job.id() == job_id:
                    self._queue.remove(job)
                    return True
        return False

    def get_by_job_id(self, job_id):
        if not self.is_empty():
            for job in self._queue:
                if job.id() == job_id:
                    return job
        return None
        pass

    def get_jobs(self):
        # TODO 作为替换原来的self.jobs属性，预留的方法
        if not self.is_empty():
            return self._queue
        return []

    def length(self):
        return len(self._queue)

    def len_by_class(self, clazz):
        return len([job for job in self._queue if isinstance(job, clazz)])

    def is_empty(self):
        if self.length() == 0:
            return True
        return False

    def look_all(self):
        if not self.is_empty():
            return [m for m in self._queue]
    pass


class JobQueue(object):
    def __init__(self, max_limit=1000):
        self._queue = []
        self._max = max_limit

    def __str__(self):
        return "***--->>>: {}".format(self._queue)

    def length(self):
        return len(self._queue)

    def len_by_class(self, clazz):
        return len([job for job in self._queue if isinstance(job, clazz)])

    def is_empty(self):
        if self.length() == 0:
            return True
        return False

    def put(self, job):
        if self.max_able():
            self._queue.insert(0, job)
        else:
            return None

    def get_by_index(self, index=-1):
        # 根据给定的索引值获取对应的job,默认获取队列内最后一个
        if not self.is_empty() and index < self.length():
            return self._queue[index]
        else:
            return None
        pass

    # def pop_by_job_id(self, job_id):
    #     if job_id:
    #         for i in self._queue:
    #             if job_id == i.id():
    #                 self._queue.remove(i)
    #                 return True
    #     else:
    #         return False

    def pop_by_index(self, index=-1):
        # pop指定索引元素，默认为队列的最后一个
        if not self.is_empty() and index < self.length():
            return self._queue.pop(index)
        else:
            return None
        pass

    def remove_by_job_id(self, job_id):
        if job_id:
            for job in self._queue:
                if job.id() == job_id:
                    self._queue.remove(job)
                    return True
        return False

    def get_by_job_id(self, job_id):
        if not self.is_empty():
            for job in self._queue:
                if job.id() == job_id:
                    return job
        return None
        pass

    def get_jobs(self):
        # TODO 作为替换原来的self.jobs属性，预留的方法
        if not self.is_empty():
            return self._queue
        return []

    def max_able(self):
        if self.length() <= self._max:
            return True
        else:
            return False
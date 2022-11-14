"""
    三种内存队列

    注意，优先级队列的对象需要实现 __lt__ 方法
"""
import queue
from palp.sequence.sequence_base import BaseSequence


# 先进先出队列
class FIFOSequence(BaseSequence):
    def __init__(self):
        self.queue = queue.Queue()

    def put(self, obj, timeout: int = None):
        """
        添加任务

        :param timeout:
        :param obj: 数据
        :return:
        """
        self.queue.put(obj, timeout=timeout)

    def get(self, timeout: int = None):
        """
        获取任务
        :return:
        """
        try:
            item = self.queue.get(timeout=timeout)
            return item
        except queue.Empty:
            return

    def empty(self):
        """
        判断队列是否为空

        :return:
        """
        return self.queue.empty()


# 后进先出队列
class LIFOSequence(FIFOSequence):
    def __init__(self):
        super().__init__()
        self.queue = queue.LifoQueue()


# 优先级队列
class PrioritySequence(LIFOSequence):
    def __init__(self):
        super().__init__()
        self.queue = queue.PriorityQueue()

    def put(self, obj, timeout: int = None):
        """
        添加任务

        :param timeout:
        :param obj: 数据
        :return:
        """
        if hasattr(obj, 'level'):
            level = obj.level
        else:
            level = 100

        self.queue.put([level, obj], timeout=timeout)

    def get(self, timeout: int = None):
        """
        获取任务（这里的 put 都必须是 [level，value] 的形式）

        :return:
        """
        try:
            item = self.queue.get(timeout=timeout)
            return item[-1]
        except queue.Empty:
            return

"""
    三种内存队列

    注意：
        python 队列中的 PriorityQueue 需要对比的类实现 __lt__ 方法（小于）不然可能会报错
"""
import queue
from palp import settings
from palp.sequence.sequence import Sequence


class FIFOMemorySequence(Sequence):
    """
        先进先出队列
    """

    def __init__(self, q: queue.Queue = None):
        self.queue = q or queue.Queue()

    def put(self, obj, block=True, timeout=None):
        """
        添加任务

        :param timeout:
        :param block: 为 false 就是 nowait
        :param obj: 数据
        :return:
        """
        self.queue.put(obj, block=block, timeout=timeout)

    def get(self, block=True, timeout=None):
        """
        获取任务

        :param block: 为 false 就是 nowait
        :param timeout:
        :return:
        """
        try:
            item = self.queue.get(block=block, timeout=timeout)
            return item
        except queue.Empty:
            return

    def empty(self):
        """
        判断队列是否为空

        :return:
        """
        return self.queue.empty()

    def qsize(self):
        """
        返回队列大小

        :return:
        """
        return self.queue.qsize()


class LIFOMemorySequence(FIFOMemorySequence):
    """
        后进先出队列
    """

    def __init__(self):
        super().__init__(q=queue.LifoQueue())


class PriorityMemorySequence(FIFOMemorySequence):
    """
        优先级队列
    """

    def __init__(self):
        super().__init__(q=queue.PriorityQueue())

    def put(self, obj, block=True, timeout=None):
        """
        添加任务

        :param block: 为 false 就是 nowait
        :param timeout:
        :param obj: 数据
        :return:
        """
        if hasattr(obj, 'priority'):
            priority = obj.priority
        else:
            priority = settings.DEFAULT_QUEUE_PRIORITY

        self.queue.put([priority, obj], block=block, timeout=timeout)

    def get(self, block=True, timeout=None):
        """
        获取任务

        :param block: 为 false 就是 nowait
        :param timeout:
        :return:
        """
        try:
            item = self.queue.get(block=block, timeout=timeout)
            return item[-1]
        except queue.Empty:
            return

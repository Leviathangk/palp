"""
    队列结构
"""
from abc import abstractmethod


class BaseSequence:

    @abstractmethod
    def put(self, obj, timeout: int = None):
        """
        添加任务

        :param timeout:
        :param obj
        :return:
        """
        pass

    @abstractmethod
    def get(self, timeout: int = None):
        """
        获取任务

        :return:
        """
        pass

    @abstractmethod
    def empty(self) -> bool:
        """
        判断队列是否为空

        :return:
        """
        pass

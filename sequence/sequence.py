"""
    消息队列
"""
from typing import Any
from abc import abstractmethod


class SequenceBase:
    """
        队列的基类
    """

    @abstractmethod
    def put(self, obj: Any, timeout: float = None) -> None:
        """
        添加任务

        :param timeout:
        :param obj
        :return:
        """
        pass

    @abstractmethod
    def get(self, timeout: float = None) -> None:
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


class Sequence:
    """
        用于外部引用：队列的基类
    """

    def put(self, obj, timeout=None):
        """
        添加任务

        :param timeout:
        :param obj
        :return:
        """
        pass

    def get(self, timeout=None):
        """
        获取任务

        :return:
        """
        pass

    def empty(self):
        """
        判断队列是否为空

        :return:
        """
        pass


class RedisSequence(Sequence):
    """
        Redis 队列的基类
    """
    def __new__(cls, *args, **kwargs):
        """
        给创建的每一个类都添加一个 redis_key 属性

        :param args:
        :param kwargs:
        """
        cls.redis_key = cls.get_redis_key()

        return object.__new__(cls)

    @classmethod
    @abstractmethod
    def get_redis_key(cls) -> str:
        """
        获取 redis 的键

        :return:
        """
        pass

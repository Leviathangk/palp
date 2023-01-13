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
    def put(self, obj: Any, timeout: float = None, **kwargs) -> None:
        """
        添加任务

        :param timeout:
        :param obj
        :return:
        """

    @abstractmethod
    def get(self, timeout: float = None, **kwargs) -> None:
        """
        获取任务

        :param timeout:
        :return:
        """

    @abstractmethod
    def empty(self) -> bool:
        """
        判断队列是否为空

        :return:
        """

    @abstractmethod
    def qsize(self) -> int:
        """
        返回队列大小

        :return:
        """


class Sequence(SequenceBase):
    """
        用于外部引用：队列的基类
    """

    def put(self, obj, block=True, timeout=None):
        """
        添加任务

        :param timeout:
        :param block:
        :param obj
        :return:
        """

    def get(self, block=True, timeout=None):
        """
        获取任务

        :param timeout:
        :param block: 为 False 时就是 get_nowait()
        :return:
        """

    def empty(self):
        """
        判断队列是否为空

        :return:
        """

    def qsize(self):
        """
        返回队列大小

        :return:
        """


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

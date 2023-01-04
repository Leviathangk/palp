"""
    过滤器
"""
import hashlib
import threading
from typing import Union, Any
from abc import abstractmethod
from palp.item.item import Item
from urllib.parse import urlencode
from palp.network.request import Request


class FilterBase:
    @abstractmethod
    def is_repeat(self, obj: Union[Request, Item], **kwargs) -> bool:
        """
        判断是否重复，必须实现不存在则添加的方法

        :param obj: request 对象或 item 对象
        :param kwargs:
        :return:
        """

    @abstractmethod
    def judge(self, f: Any, fingerprint: str) -> bool:
        """
        进行判断

        :param f: 判断条件或方法之类
        :param fingerprint: 指纹
        :return:
        """

    @staticmethod
    def fingerprint(obj: Union[Request, Item]) -> str:
        """
        获取能够代表唯一的字符串

        :param obj: request 对象或 item 对象
        :return:
        """
        if isinstance(obj, Request):
            if obj.method == 'GET':
                filter_str = urlencode(obj.params or {})
            elif obj.method == 'POST':
                filter_str = urlencode(obj.params or {}) + urlencode(obj.data or {}) + urlencode(obj.json or {})
            else:
                filter_str = ''

            filter_str = obj.method + obj.url + filter_str
        else:
            filter_str = obj.to_json()

        return hashlib.md5(filter_str.encode()).hexdigest()


class FilterLock:
    """
        线程锁，用于数据同步（filter 专用）
    """
    lock = threading.RLock()

    def __init__(self, timout: int = 5):
        """
        锁的时间

        :param timout:
        """
        self.timeout = timout

    def __enter__(self):
        self.__class__.lock.acquire(timeout=self.timeout)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__class__.lock.release()

"""
    过滤器
"""
import hashlib
import threading
from typing import Union
from abc import abstractmethod
from urllib.parse import urlencode
from palp.item.item_base import BaseItem
from palp.network.request import Request


class BaseFilter:
    @abstractmethod
    def is_repeat(self, obj: Union[Request, BaseItem], **kwargs) -> bool:
        """
        判断是否重复，必须实现不存在则添加的方法

        :param obj: request 对象或 item 对象
        :return:
        """
        pass

    @abstractmethod
    def judge(self, fingerprint, f) -> bool:
        """
        进行判断

        :param fingerprint: 指纹
        :param f: 判断条件或方法之类
        :return:
        """
        pass

    @staticmethod
    def fingerprint(obj: Union[Request, BaseItem]) -> str:
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


# filter 专用的锁
class FilterLock:
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

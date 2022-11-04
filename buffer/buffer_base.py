"""
    item 处理

    可自定义缓存数量，一次性进入 pipeline_save 函数入库
"""
import threading
from abc import abstractmethod
from palp.item.item_base import BaseItem


class BaseItemBuffer(threading.Thread):
    PIPELINE = []

    @classmethod
    def from_settings(cls):
        """
        加载设置

        :return:
        """
        pass

    @abstractmethod
    def run(self) -> None:
        """
        入口函数

        :return:
        """
        pass

    @abstractmethod
    def pipeline_in(self, item: BaseItem):
        """
        存放、清洗 item

        :param item:
        :return:
        """
        pass

    @abstractmethod
    def pipeline_save(self):
        """
        处理入库

        :return:
        """
        pass

    @abstractmethod
    def pipeline_close(self):
        """
        spider 结束时运行

        :return:
        """
        pass

    @property
    @abstractmethod
    def buffer_size(self):
        """
        返回 buffer 大小

        :return:
        """
        return

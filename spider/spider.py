"""
    单机 spider
"""
from palp import settings
from threading import Thread
from abc import abstractmethod
from palp.spider.spider_base import BaseSpider
from palp.buffer.buffer_item import ItemBuffer


class Spider(BaseSpider, Thread):
    def __init__(self, thread_count=None, request_filter=False, item_filter=False):
        """

        :param thread_count: 线程数量
        :param request_filter: 开启请求过滤，不然 filter_repeat 无效
        :param item_filter: 开启 item 过滤
        """
        setattr(settings, 'SPIDER_TYPE', 1)
        super().__init__(thread_count, request_filter, item_filter)

    @abstractmethod
    def start_requests(self) -> None:
        """
        起始函数

        :return:
        """
        pass

    def spider_logic(self):
        """
        spider 处理逻辑

        :return:
        """
        # 一个线程处理 item
        ItemBuffer.from_settings()
        self._item_buffer = ItemBuffer(spider=self, q=self._queue_item)
        self._item_buffer.start()

        # 分发任务
        self.distribute_task()

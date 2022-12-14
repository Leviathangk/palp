"""
    单机 spider（不支持分布式）
"""
from palp import settings
from abc import abstractmethod
from palp.spider.spider import Spider
from palp.decorator.decorator_spider_middleware import SpiderMiddlewareDecorator
from palp.sequence.sequence_memory import PriorityMemorySequence, FIFOMemorySequence


class LocalSpider(Spider):
    """
        单机 spider（不支持分布式）
    """

    def __init__(self, thread_count: int = None, request_filter: bool = False, item_filter: bool = False):
        super().__init__(thread_count, request_filter, item_filter)
        setattr(settings, 'SPIDER_TYPE', 1)

        self.queue = PriorityMemorySequence()  # 请求队列
        self.queue_item = FIFOMemorySequence()  # item 队列

    @abstractmethod
    def start_requests(self) -> None:
        """
        起始函数

        :return:
        """
        pass

    @SpiderMiddlewareDecorator()
    def run(self) -> None:
        self.start_controller()  # 任务处理
        self.start_distribute()  # 分发任务
        self.wait_distribute_thread_done()  # 等待任务分发完毕

"""
    单机 spider（不支持分布式）
"""
from palp import settings
from abc import abstractmethod
from palp.spider.spider import Spider
from palp.network.request import Request
from palp.tool.short_module import import_module
from palp.decorator.decorator_spider_wait import SpiderWaitDecorator
from palp.decorator.decorator_spider_once import SpiderOnceDecorator
from palp.decorator.decorator_spider_middleware import SpiderMiddlewareDecorator
from palp.sequence.sequence_memory import PriorityMemorySequence, FIFOMemorySequence


class LocalSpider(Spider):
    """
        单机 spider（不支持分布式）
    """

    def __init__(self, thread_count: int = None, request_filter: bool = False, item_filter: bool = False):
        super().__init__(thread_count, request_filter, item_filter)
        setattr(settings, 'SPIDER_TYPE', 1)

        queue_module = settings.REQUEST_QUEUE[settings.SPIDER_TYPE][settings.REQUEST_QUEUE_MODE]
        self.queue = import_module(queue_module)[0]  # 请求队列
        self.queue = PriorityMemorySequence()  # 请求队列
        self.queue_item = FIFOMemorySequence()  # item 队列
        self.queue_borrow = FIFOMemorySequence()  # 信息传递队列

    @abstractmethod
    def start_requests(self) -> None:
        """
        起始函数

        :return:
        """

    def borrow_request(self, request: Request):
        """
        开启 REQUEST_BORROW 时，用来主动使用资源

        :param request: 新的请求，决定何时调用
        :return:
        """
        # 空 cookie_jar 即视为新的请求，添加 cookie_jar
        if not request.cookie_jar and request.keep_cookie:
            recycle_data = self.queue_borrow.get(block=False)
            if recycle_data:
                if 'cookie_jar' in recycle_data:
                    request.cookie_jar = recycle_data['cookie_jar']

    def recycle_request(self, request: Request):
        """
        开启 REQUEST_BORROW 时，用来主动回收资源，一般在程序执行最后一个函数后调用

        尽量是 request 含有的 key

        :param request: 旧的请求。回收指定资源
        :return:
        """
        recycle_data = {}

        # 回收 cookie
        if request.cookie_jar:
            recycle_data.update({'cookie_jar': request.cookie_jar})

        # 发送回收的资源
        if recycle_data:
            self.queue_borrow.put(recycle_data)

    @SpiderMiddlewareDecorator()
    @SpiderOnceDecorator()
    @SpiderWaitDecorator()
    def run(self) -> None:
        self.start_controller()  # 任务处理
        self.start_distribute()  # 分发任务
        self.wait_distribute_thread_done()  # 等待任务分发完毕

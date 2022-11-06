"""
    处理爬虫 yield 的请求、item 处理
"""
import inspect
import traceback
from urllib.parse import urlparse

from loguru import logger
from palp import settings
from threading import Thread
from palp.network.request import Request
from palp.item.item_base import BaseItem
from palp.exception import exception_drop
from palp.tool.short_module import import_module
from palp.sequence.sequence_base import BaseSequence


class Parser(Thread):
    REQUEST_MIDDLEWARE = []

    def __init__(self, q: BaseSequence, q_item: BaseSequence, spider):
        """

        :param q: request 队列
        :param q_item: item 队列
        :param spider: 运行的爬虫
        """
        super().__init__()
        self.queue = q
        self.queue_item = q_item
        self.spider = spider

        self.waiting = False  # parser 执行状态，如果拿到空任务就是在等待
        self.stop = False  # 是否暂停

    @classmethod
    def from_settings(cls):
        """
        导入过滤设置

        :return:
        """
        request_filter_middleware = import_module(
            settings.REQUEST_FILTER_MIDDLEWARE[settings.SPIDER_TYPE][settings.FILTERING_MODE])
        cls.REQUEST_MIDDLEWARE = request_filter_middleware + import_module(settings.REQUEST_MIDDLEWARE)

    def run(self):
        """
        函数执行入口

        :return:
        """
        while not self.stop:
            task = self.queue.get()

            try:
                if task is None:
                    self.waiting = True
                    continue

                # 将 requests 还原
                elif isinstance(task, Request) and task.callback and hasattr(self.spider, str(task.callback)):
                    task.callback = eval(f"self.spider.{task.callback}")

                self.waiting = False
                self.parse_task(task=task)
            except exception_drop.DropRequestException:
                logger.debug(f"丢弃请求：{task}")
            except Exception as e:
                # spider 报错处理
                for middleware in self.spider.SPIDER_MIDDLEWARE:
                    middleware.spider_error(self.spider, e.__class__.__name__, traceback.format_exc())

    def parse_task(self, task, request: Request = None):
        """
        解析处理任务

        :param task: 任务
        :param request: 上一个的请求
        :return:
        """
        # 判断 yield 的类型
        if isinstance(task, Request):
            if request:
                self.add_new_request(task, request)
            else:
                self.run_requests(task)
        elif isinstance(task, BaseItem):
            self.queue_item.put(task)
        else:
            logger.warning(f"捕获到非法 yield：{task}")

    def add_new_request(self, new_request: Request, old_request: Request):
        """
        添加新的请求到队列中

        :param new_request:
        :param old_request:
        :return:
        """
        # 自动拼接 url（根据上一个请求的域名）
        if not new_request.url.startswith('http'):
            prefix = urlparse(old_request.url)

            if new_request.url.startswith('//'):
                new_request.url = new_request.url.lstrip('/')
                new_request.url = prefix.scheme + '://' + new_request.url
            else:
                new_request.url = new_request.url.lstrip('/')
                new_request.url = prefix.scheme + '://' + prefix.netloc + '/' + new_request.url

        new_request.callback = new_request.callback.__name__  # 转成字符串，不然无法序列化
        new_request.session = old_request.session  # 续上上一个的 session
        new_request.cookie_jar = old_request.cookie_jar  # 续上上一个的 cookie_jar
        self.queue.put(new_request)

    def run_requests(self, request: Request):
        """
        处理 yield 的 Request

        :param request:
        :return:
        """
        # 请求发起前的处理
        for middleware in self.__class__.REQUEST_MIDDLEWARE:
            middleware.request_in(self.spider, request)

        # 处理请求
        callback = None
        response = None
        failed_times = 0
        while failed_times < settings.REQUEST_RETRY_TIMES:
            try:
                callback, response = request.send()
                break
            except exception_drop.DropRequestException:
                raise
            except Exception as e:
                failed_times += 1

                # 出现错误可直接处理，并返回新的请求，同时阻断当前错误请求传播
                for middleware in self.__class__.REQUEST_MIDDLEWARE:
                    new_request = middleware.request_error(self.spider, request, e.__class__.__name__,
                                                           traceback.format_exc())
                    if new_request is None:
                        pass
                    elif isinstance(new_request, Request):
                        self.add_new_request(new_request=new_request, old_request=request)
                        raise exception_drop.DropRequestException()
                    else:
                        logger.warning("request_error 仅支持 Request 返回值！")

            # 失败达到最大次数直接丢弃
            if failed_times >= settings.REQUEST_RETRY_TIMES:
                for middleware in self.__class__.REQUEST_MIDDLEWARE:
                    middleware.request_failed(self.spider, request)
                return

        # 请求结束的回调（可在此时判断返回值是否合理，不合理可在此重新构造请求，同时阻断当前请求传播）
        for middleware in self.__class__.REQUEST_MIDDLEWARE:
            new_request = middleware.request_close(self.spider, request, response)
            if new_request is None:
                pass
            elif isinstance(new_request, Request):
                self.add_new_request(new_request=new_request, old_request=request)
                raise exception_drop.DropRequestException()
            else:
                logger.warning("request_close 仅支持 Request 返回值！")

        # 继续监控下次yield
        if callback is not None:
            if inspect.isgeneratorfunction(callback):  # 很好用的库，判断是否是 yield 函数
                for task in callback(request, response):
                    self.parse_task(task=task, request=request)
            else:
                callback(request, response)

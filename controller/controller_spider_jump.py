"""
    jump spider 控制器
"""
import inspect
from palp import settings
from loguru import logger
from typing import Union, List, Callable
from palp.network.request import Request
from palp.network.response import Response
from palp.sequence.sequence import Sequence
from palp.exception import DropRequestException
from palp.middleware import RequestRecordMiddleware
from palp.decorator.decorator_lock import FuncLockSharedDecorator


class JumpController:
    REQUEST_MIDDLEWARE = {
        'RequestRecordMiddleware': RequestRecordMiddleware()  # 记录请求
    }

    def __init__(self, q: Sequence, request_middleware: Union[List[Callable], Callable], spider):
        """

        :param q: 请求队列
        :param request_middleware: 请求中间件
        :param spider: jump spider
        """
        # 导入设置
        if request_middleware is None:
            request_middleware = []
        elif not isinstance(request_middleware, list):
            request_middleware = [request_middleware]

        # 实例化
        for i, m in enumerate(request_middleware):
            if m.__name__ == 'RequestRecordMiddleware':
                continue
            if m not in self.__class__.REQUEST_MIDDLEWARE:
                request_middleware[i] = m()
                self.__class__.REQUEST_MIDDLEWARE[m] = request_middleware[i]
            else:
                request_middleware[i] = self.__class__.REQUEST_MIDDLEWARE[m]

        self.queue = q
        self.spider = spider
        self.request_middleware = request_middleware + [JumpController.REQUEST_MIDDLEWARE['RequestRecordMiddleware']]

    def run(self):
        """
        执行流程

        :return:
        """
        request = None

        try:
            while True:
                task = self.queue.get(timeout=0.5)

                try:
                    if task is None:
                        break
                    elif not isinstance(task, Request):
                        continue

                    request = task
                    self.run_requests(request=task)
                except DropRequestException as e:
                    logger.warning(f"丢弃请求：{e}")
        finally:
            self.change_record()

            if request:
                self.spider.jump_out(request)

    def add_new_request(self, new_request: Request, old_request: Request, response: Response):
        """
        添加新的请求到队列中

        :param new_request:
        :param old_request:
        :param response:
        :return:
        """
        # 自动衔接 meta
        if old_request.meta:
            new_request.meta.update(old_request.meta)

        # 自动拼接 url
        if not new_request.url.startswith('http') and response:
            new_request.url = response.urljoin(new_request.url)

        # 添加请求必须参数：新 cookieJar 会覆盖老 cookieJar
        if not new_request.cookie_jar:
            new_request.cookie_jar = old_request.cookie_jar  # 续上上一个的 cookie_jar

        # 修改优先级，深层的函数应该优先处理，避免积压不前（深度爬取）
        if settings.REQUEST_QUEUE_MODE == 3:
            new_request.priority = old_request.priority - 1

        self.queue.put(new_request)

    def run_requests(self, request: Request):
        """
        处理 yield 的 Request

        :param request:
        :return:
        """
        # 请求发起前的处理
        for middleware in self.request_middleware:
            middleware.request_in(self.spider, request)

        # 处理请求
        response = None
        failed_times = 0
        while failed_times < settings.REQUEST_RETRY_TIMES:
            try:
                response = request.send()
                break
            except Exception as e:
                failed_times += 1

                # 出现错误可直接处理，并返回新的请求，同时阻断当前错误请求传播
                for middleware in self.request_middleware:
                    new_request = middleware.request_error(self.spider, request, e)
                    if new_request is None:
                        continue
                    elif isinstance(new_request, Request):
                        self.add_new_request(new_request=new_request, old_request=request, response=response)
                        raise DropRequestException(middleware.__class__.__name__, str(request))
                    else:
                        logger.warning("request_error 仅支持 Request 返回值！")

            # 失败达到最大次数直接丢弃
            if failed_times >= settings.REQUEST_RETRY_TIMES:
                for middleware in self.request_middleware:
                    middleware.request_failed(self.spider, request)
                return

        # 请求结束的回调（可在此时判断返回值是否合理，不合理可在此重新构造请求，同时阻断当前请求传播）
        for middleware in self.request_middleware:
            new_request = middleware.request_close(self.spider, request, response)
            if new_request is None:
                continue
            elif isinstance(new_request, Request):
                self.add_new_request(new_request=new_request, old_request=request, response=response)
                raise DropRequestException(middleware.__class__.__name__, str(request))
            else:
                logger.warning("request_close 仅支持 Request 返回值！")

        # 继续监控下次 yield
        if request.callback and isinstance(request.callback, str) and hasattr(self.spider, request.callback):
            callback = getattr(self.spider, request.callback)

            if inspect.isgeneratorfunction(callback):  # 很好用的库，判断是否是 yield 函数
                for task in callback(request, response):
                    if isinstance(task, Request):
                        self.add_new_request(new_request=task, old_request=request, response=response)
            else:
                callback(request, response)

    @FuncLockSharedDecorator(timeout=1)
    def change_record(self):
        """
        修改记录

        :return:
        """
        self.spider.main_spider.spider_record['all'] += self.spider.spider_record['all']
        self.spider.main_spider.spider_record['failed'] += self.spider.spider_record['failed']
        self.spider.main_spider.spider_record['succeed'] += self.spider.spider_record['succeed']

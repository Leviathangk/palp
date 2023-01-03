"""
    jump spider（本地执行，用于处理比较频繁的循环事件，完全独立正常的 spider）

    jump spider 内置 spider_start、spider_close
    jump spider 参数 request_middleware 可传请求中间件

    注意：
        jump spider 不走 spider、request 中间件、不走 记录装饰器
        jump spider 不能 yield item yield 的都不会处理
        jump spider 最后会执行 jump_out 合并 cookie、meta，可以自定义
"""
import inspect
from palp import settings
from abc import abstractmethod
from typing import Union, List, Callable
from palp.network.request import Request
from palp.network.response import Response
from palp.tool.short_module import import_module
from palp.exception import NotGeneratorFunctionError
from palp.controller.controller_spider_jump import JumpController


class JumpSpider:
    """
        jump spider（用于处理比较频繁的循环事件）

        注意：不走 spider 中间件，不处理 item
    """

    def __init__(self,main_spider, request: Request, request_middleware: Union[List[Callable], Callable] = None, **kwargs):
        """

        :param request: jump 之后需要执行的请求
        :param request_middleware: 请求中间件
        :param kwargs: 需要被 self.xxx 访问到的参数
        """
        self.main_spider = main_spider
        self.request = request
        self.request_middleware = request_middleware
        self.spider_record = {'all': 0, 'failed': 0, 'succeed': 0}
        self.queue = import_module(settings.REQUEST_QUEUE[1][settings.REQUEST_QUEUE_MODE])[0]  # 请求队列

        # 导入一下自定义设置
        for key, value in kwargs.items():
            setattr(self, key, value)

    def spider_start(self) -> None:
        """
        spider 开始时的操作

        :param spider:
        :return:
        """

    def spider_close(self) -> None:
        """
        spider 开始时的操作

        :param spider:
        :return:
        """

    @abstractmethod
    def start_requests(self) -> None:
        """
        起始函数

        :return:
        """

    def start_distribute(self) -> None:
        """
        刚开始的分发任务

        :return:
        """
        # 校验是否是生成器函数
        if not inspect.isgeneratorfunction(self.start_requests):
            raise NotGeneratorFunctionError("start_requests 必须 yield Request!")

        # 检查起始函数发出请求
        for request in self.start_requests():
            if not isinstance(request, Request):
                raise ValueError("start_requests 仅支持 yield Request")

            # 起始函数无 callback 默认添加
            if request.callback is None:
                request.callback = self.parse

            self.queue.put(request)

    def parse(self, request: Request, response: Response) -> None:
        """
        默认的解析函数（仅 start_requests 默认的）

        @result:
        """

    def run(self) -> None:
        """
        执行 jump spider

        :return:
        """
        self.spider_start()

        try:
            # 分发任务
            self.start_distribute()

            # 执行流程
            JumpController(q=self.queue, request_middleware=self.request_middleware, spider=self).run()
        finally:
            self.spider_close()

    def jump_out(self, request: Request):
        """
        jump spider 执行结束之后，将会调用合并 cookie、meta

        :param request:
        :return:
        """
        self.request.cookie_jar.update(request.cookie_jar)
        if self.request.meta:
            self.request.meta.update(request.meta)
        else:
            self.request.meta = request.meta

    def __setattr__(self, key, value):
        """
        设置属性

        :param key:
        :param value:
        :return:
        """
        self.__dict__[key] = value

    def __getattr__(self, key):
        """
        获取属性

        :param key:
        :return:
        """
        if key not in self.__dict__:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")

        return self.__dict__[key]

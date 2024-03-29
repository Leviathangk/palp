"""
    spider 流程控制器：处理整个爬虫的处理过程流转
"""
import dill
import inspect
import traceback
from loguru import logger
from palp import settings
from threading import Thread
from palp.item.item import Item
from palp.network.request import Request
from palp.network.response import Response
from palp.sequence.sequence import Sequence
from palp.exception import DropRequestException
from palp.tool.short_module import import_module, sort_module


class SpiderController(Thread):
    REQUEST_MIDDLEWARE = []

    def __new__(cls, *args, **kwargs):
        """
        实例化之前加载设置

        :param args:
        :param kwargs:
        """
        if not SpiderController.REQUEST_MIDDLEWARE:
            SpiderController.from_settings()

        return object.__new__(cls)

    def __init__(self, q: Sequence, q_item: Sequence, spider):
        """

        :param q: request 队列
        :param q_item: item 队列
        :param spider: 运行的爬虫
        """
        super().__init__()
        self.queue = q
        self.spider = spider
        self.queue_item = q_item

        self.waiting = False  # 执行状态，如果拿到空任务就是在等待
        self.stop = False  # 是否暂停

    @classmethod
    def from_settings(cls):
        """
        导入设置

        :return:
        """
        modules = sort_module(
            cls_dict=settings.REQUEST_MIDDLEWARE,
            palp_cls_dict=settings.PALP_REQUEST_MIDDLEWARE,
            cls_mapping={
                'REQUEST_FILTER_MIDDLEWARE': settings.REQUEST_FILTER_MIDDLEWARE[settings.SPIDER_TYPE][
                    settings.FILTERING_MODE]
            }
        )

        SpiderController.REQUEST_MIDDLEWARE = import_module(modules)

    def run(self):
        """
        函数执行入口

        :return:
        """
        while not self.stop:
            task = self.queue.get(timeout=1)

            try:
                if task is None:
                    self.waiting = True
                    continue

                self.waiting = False
                self.parse_task(task=task)
            except DropRequestException as e:
                logger.warning(f"丢弃请求：{e}")
            except Exception as e:
                if settings.SPIDER_STOP_ON_ERROR:
                    raise

                # spider 报错处理
                for middleware in self.spider.SPIDER_MIDDLEWARE:
                    middleware.spider_error(self.spider, e)

    def parse_task(self, task, request: Request = None, response: Response = None):
        """
        解析处理任务

        :param task: 任务
        :param request: 上一个的请求
        :param response:
        :return:
        """
        # 判断 yield 的类型
        if isinstance(task, Request):
            if request:
                self.add_new_request(task, request, response)
            elif task.jump_spider:
                self.run_jump_spider(task)
            else:
                self.run_requests(task)
        elif issubclass(task.__class__, Item):
            self.queue_item.put(task)
        else:
            logger.warning(f"捕获到非法 yield：{task}")

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
        # 判断是否要借 资源
        if settings.REQUEST_BORROW:
            self.spider.borrow_request(request=request)

        # 请求发起前的处理
        for middleware in self.__class__.REQUEST_MIDDLEWARE:
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
                for middleware in self.__class__.REQUEST_MIDDLEWARE:
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
                for middleware in self.__class__.REQUEST_MIDDLEWARE:
                    middleware.request_failed(self.spider, request)
                return

        # 请求结束的回调（可在此时判断返回值是否合理，不合理可在此重新构造请求，同时阻断当前请求传播）
        for middleware in self.__class__.REQUEST_MIDDLEWARE:
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
                    self.parse_task(task=task, request=request, response=response)
            else:
                callback(request, response)

    def run_jump_spider(self, request: Request):
        """
        处理 jump spider

        :param request:
        :return:
        """
        try:
            # 提取参数
            jump_spider = request.jump_spider
            jump_spider_kwargs = request.jump_spider_kwargs or {}
            jump_request_middleware = request.jump_request_middleware or []

            # 执行 jump_spider
            jump_spider(
                main_spider=self.spider,
                request=request,
                request_middleware=jump_request_middleware,
                **jump_spider_kwargs
            ).run()

            # 执行成功则参数置空，并发起需要的请求
            request.jump_spider = None
            request.jump_spider_kwargs = None
            request.jump_request_middleware = None

            # 修改优先级，深层的函数应该优先处理，避免积压不前（深度爬取）
            if settings.REQUEST_QUEUE_MODE == 3:
                request.priority -= 1

            self.queue.put(request)
        except Exception as e:
            traceback.print_exc()

            # 失败直接放入失败中间件，不会重试
            for middleware in self.__class__.REQUEST_MIDDLEWARE:
                middleware.request_failed(self.spider, request)

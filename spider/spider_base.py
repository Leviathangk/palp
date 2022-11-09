"""
    spider 基类
"""
import sys
import time
import types
import inspect
import requests
import traceback
from pathlib import Path
from loguru import logger
from palp import settings
from threading import Thread
from palp.parser import Parser
from typing import List, Union
from palp.network.request import Request
from palp.network.response import Response
from requests.cookies import RequestsCookieJar
from palp.tool.short_module import import_module
from palp.exception.exception_error import NotGeneratorFunctionError
from palp.sequence.sequence_memory import FIFOSequence as FIFOSequenceMemory
from palp.sequence.sequence_redis_item import FIFOSequence as FIFOSequenceRedis


class BaseSpider(Thread):
    spider_name = None  # 用户输入的名字
    spider_settings: Union[types.ModuleType, dict] = None  # 用来指定爬虫单独的配置，可以是一个引入的 settings.py 模块 或 字典
    SPIDER_MIDDLEWARE: List[types.ModuleType] = []

    def __init__(self, thread_count: int = None, request_filter: bool = False, item_filter: bool = False):
        super().__init__()
        # 加载设置
        self.from_settings()

        # 加载快捷的设置
        if thread_count:
            setattr(settings, 'SPIDER_THREAD_COUNT', thread_count)
        if request_filter:
            setattr(settings, 'REQUEST_FILTER', request_filter)
        if item_filter:
            setattr(settings, 'ITEM_FILTER', item_filter)

        # 获取队列
        queue_module = settings.REQUEST_QUEUE[settings.SPIDER_TYPE][settings.REQUEST_MODE]
        self._queue = import_module(queue_module)[0]  # 存储 请求
        if settings.SPIDER_TYPE == 1:
            self._queue_item = FIFOSequenceMemory()  # 存储 item
        else:
            self._queue_item = FIFOSequenceRedis()

        self._parser_list = []  # 存储所有的解析器
        self._item_buffer = None  # item buffer 线程
        self.spider_done = False  # 爬虫是否运行结束
        self.spider_master = False  # 是否是主机器

    @classmethod
    def from_settings(cls) -> None:
        """
        spider 启动时的自定义配置解析自定义的配置文件

        :return:
        """
        # 修改日志
        if settings.LOG_SAVE:
            log_path = Path(settings.LOG_PATH).joinpath(cls.__name__)
            log_path.mkdir(parents=True, exist_ok=True)

            logger.remove()
            logger.add(
                sink=log_path.joinpath(f'{cls.__name__}.log'),
                enqueue=True,
                backtrace=True,
                diagnose=True,
                rotation=settings.LOG_ROTATION,
                compression=settings.LOG_COMPRESSION,
                level=settings.LOG_LEVEL,
                retention=settings.LOG_RETENTION,
            )

            # 让日志同时能够输出
            if settings.LOG_SHOW:
                logger.add(sys.stdout, level=settings.LOG_LEVEL)

        # 处理每个爬虫单独的设置
        if isinstance(cls.spider_settings, types.ModuleType):
            for key, value in cls.spider_settings.__dict__.items():
                if not key.startswith('__'):
                    setattr(settings, key, value)
        elif isinstance(cls.spider_settings, dict):
            for key, value in cls.spider_settings.items():
                setattr(settings, key, value)
        elif cls.spider_settings is None:
            pass
        else:
            logger.warning("不受支持的设置格式，仅支持模块或者字典！")

        # 引入中间件
        cls.SPIDER_MIDDLEWARE = import_module(settings.SPIDER_MIDDLEWARE)

        # 导入一次连接，防止连接不可用
        from palp import conn
        if settings.SPIDER_TYPE == 2:
            if conn.redis_conn is None:
                raise ConnectionError('redis 未连接！')
            else:
                conn.redis_conn.info()

    def start_requests(self) -> None:
        """
        初始请求的发出

        @result: yield Request()
        """
        pass

    def parse(self, request: Request, response: Response) -> None:
        """
        默认的解析函数（仅 start_requests 默认的）

        @result:
        """
        pass

    def distribute_task(self) -> None:
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

            # 先改成名字，不然后续无法序列化
            request.callback = request.callback.__name__

            # 为每一个起始函数添加一个 session、cookie_jar
            request.session = requests.session()
            request.cookie_jar = RequestsCookieJar()

            self._queue.put(request)

    def wait_parser_done(self) -> None:
        """
        等待线程执行结束

        :return:
        """
        while True:
            if self.all_parser_is_waiting():
                logger.debug("所有线程都已挂起，即将停止")
                self.stop_all_parser()
                break
            elif self.all_parser_is_done():
                break
            else:
                time.sleep(1)  # 不加延迟将会导致性能问题

        self.spider_done = True

    def wait_item_buffer_done(self) -> None:
        """
        等待 item buffer 结束

        :return:
        """
        while True:
            if not self._item_buffer.is_alive():
                break
            else:
                time.sleep(1)

    def stop_all_parser(self):
        """
        停止所有 parser 运行

        :return:
        """
        for p in self._parser_list:
            p.stop = True

        while True:
            if self.all_parser_is_done():
                break

    def all_parser_is_waiting(self) -> bool:
        """
        是否所有 parser 都没事干

        :return:
        """
        waiting_status = True

        for p in self._parser_list:
            if not p.waiting:
                waiting_status = False
                break

        return waiting_status

    def all_parser_is_done(self) -> bool:
        """
        判断所有 parser 是否已经结束

        :return:
        """

        done_status = True

        for p in self._parser_list:
            if p.is_alive():
                done_status = False
                break

        return done_status

    def spider_logic(self) -> None:
        """
        子类实现爬虫逻辑的地方

        :return:
        """
        pass

    def run(self) -> None:
        """
        启动入口

        :return:
        """
        try:
            # spider 开始执行前的处理
            for middleware in self.__class__.SPIDER_MIDDLEWARE:
                middleware.spider_start(self)

            # 启动对应的线程
            Parser.from_settings()
            for i in range(settings.SPIDER_THREAD_COUNT):
                parser = Parser(q=self._queue, q_item=self._queue_item, spider=self)
                self._parser_list.append(parser)
                parser.start()

            # spider 逻辑
            self.spider_logic()

        except Exception as e:
            for middleware in self.__class__.SPIDER_MIDDLEWARE:
                middleware.spider_error(self, e.__class__.__name__, traceback.format_exc())
        finally:
            # 等待线程执行完毕
            self.wait_parser_done()

            # 等待 item buffer 执行完毕
            if settings.SPIDER_TYPE == 1 or (settings.SPIDER_TYPE == 2 and self.spider_master):
                self.wait_item_buffer_done()

            logger.debug("无任务，爬虫结束")

            # spider 结束之后的处理
            for middleware in self.__class__.SPIDER_MIDDLEWARE:
                middleware.spider_close(self)

    @property
    def name(self) -> str:
        """
        获取 spider 的名字

        :return:
        """

        return self.__class__.spider_name or self.__class__.__name__

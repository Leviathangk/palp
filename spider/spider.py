"""
    spider 基类

    注意：要明白类的赋值操作、修改操作的概念
    赋值操作：给类本身进行赋值
    修改操作：类本身赋值后，是基于类本身修改，类本身未赋值，那么就会向父类进行查找，修改的就是父类
"""
import sys
import time
import uuid
import types
import inspect
import threading
from pathlib import Path

import dill

from palp import settings
from loguru import logger
from abc import abstractmethod
from typing import Union, List
from gsender import EmailSender
from palp.network.request import Request
from palp.network.response import Response
from palp.controller import SpiderController, ItemController
from palp.tool.short_module import sort_module, import_module
from palp.decorator.decorator_run_func_by_thread import RunByThreadDecorator


class SpiderBase(threading.Thread):
    spider_name = None  # 用户输入的名字
    spider_domains = []  # 允许 spider 通过的域名，默认都可以
    spider_settings: Union[types.ModuleType, dict] = None  # 用来指定爬虫单独的配置，可以是一个引入的 settings.py 模块 或 字典
    SPIDER_MIDDLEWARE: List[types.ModuleType] = []

    def __new__(cls, *args, **kwargs):
        """
        实例化之前加载设置

        :param args:
        :param kwargs:
        """
        if not cls.SPIDER_MIDDLEWARE:
            cls.from_settings()

        return object.__new__(cls)

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
        modules = sort_module(
            cls_dict=settings.SPIDER_MIDDLEWARE,
            palp_cls_dict=settings.PALP_SPIDER_MIDDLEWARE
        )

        cls.SPIDER_MIDDLEWARE = import_module(modules)

        # 创建连接，检查连接，防止连接不可用
        from palp import conn

        if settings.SPIDER_TYPE != 1 and conn.redis_conn is None:
            raise ConnectionError('redis 未连接！')
        if conn.redis_conn:
            conn.redis_conn.info()
        if settings.MYSQL_HOST:
            conn.mysql_conn.connection()
        if settings.PG_HOST:
            conn.pg_conn.connection()
        if settings.MONGO_HOST:
            conn.mongo_conn.conn.server_info()

        # 检查其余可用性
        # 邮件是否可用
        if settings.EMAIL_USER and settings.EMAIL_PWD:
            EmailSender(user=settings.EMAIL_USER, pwd=settings.EMAIL_PWD).check_availability()

    def __init__(self, thread_count: int = None, request_filter: bool = False, item_filter: bool = False):
        super().__init__()
        # 加载快捷的设置
        if thread_count:
            setattr(settings, 'REQUEST_THREADS', thread_count)
        if request_filter:
            setattr(settings, 'REQUEST_FILTER', request_filter)
        if item_filter:
            setattr(settings, 'ITEM_FILTER', item_filter)

        self.queue = None  # 请求队列
        self.queue_item = None  # item 队列
        self.spider_done = False  # 爬虫是否运行结束
        self.item_controller_list = []  # 存储所有的解析器
        self.spider_controller_list = []  # 存储所有的解析器
        self.distribute_thread_list = []  # 存储所有任务分发线程

        self.spider_record = {'all': 0, 'failed': 0, 'succeed': 0}  # 爬取情况记录
        self.spider_uuid = uuid.uuid1().hex  # uuid 用作线上区分

    def start_requests(self) -> None:
        """
        初始请求的发出

        @result: yield Request()
        """

    def parse(self, request: Request, response: Response) -> None:
        """
        默认的解析函数（仅 start_requests 默认的）

        @result:
        """

    def wait_distribute_thread_done(self) -> None:
        """
        等待所有任务分发线程执行结束

        :return:
        """
        while True:
            for distribute_thread in self.distribute_thread_list.copy():
                if not distribute_thread.is_alive():
                    self.distribute_thread_list.remove(distribute_thread)

            if len(self.distribute_thread_list) == 0:
                break

            time.sleep(0.1)

    def wait_spider_controller_done(self) -> None:
        """
        等待线程执行结束

        :return:
        """
        while True:
            if self.all_spider_controller_is_waiting():
                logger.debug("所有线程都已挂起，即将停止")
                self.stop_all_spider_controller()
                break
            elif self.all_spider_controller_is_done():
                break

            time.sleep(0.1)  # 不加延迟将会导致性能问题

    def wait_item_controller_done(self) -> None:
        """
        等待 item buffer 结束

        :return:
        """
        while True:
            for item_controller in self.item_controller_list.copy():
                if not item_controller.is_alive():
                    self.item_controller_list.remove(item_controller)

            if len(self.item_controller_list) == 0:
                break

            time.sleep(0.1)

    def stop_all_spider_controller(self) -> None:
        """
        停止所有 spider_controller 运行

        :return:
        """
        for p in self.spider_controller_list:
            p.stop = True

        while True:
            if self.all_spider_controller_is_done():
                break

            time.sleep(0.1)

    def all_distribute_thread_is_done(self) -> bool:
        """
        是否分发任务已经完成

        :return:
        """
        done_status = True

        for p in self.distribute_thread_list:
            if p.is_alive():
                done_status = False
                break

        return done_status

    def all_spider_controller_is_waiting(self) -> bool:
        """
        是否所有 spider_controller 都没事干

        :return:
        """
        waiting_status = True

        for p in self.spider_controller_list.copy():
            if not p.is_alive():
                self.spider_controller_list.remove(p)  # 避免死线程导致程序无法退出
                continue

            if not p.waiting:
                waiting_status = False
                break

        return waiting_status

    def all_spider_controller_is_done(self) -> bool:
        """
        判断所有 spider_controller 是否已经结束

        :return:
        """

        done_status = True

        for p in self.spider_controller_list:
            if p.is_alive():
                done_status = False
                break

        if done_status:
            self.spider_done = True

        return done_status

    @RunByThreadDecorator(daemon=True)
    def start_distribute(self) -> None:
        """
        刚开始的分发任务

        :return:
        """
        # 检查是否是 yield 函数，不是不报错，避免只是执行失败的
        if inspect.isgeneratorfunction(self.start_requests):
            # 检查起始函数发出请求
            for request in self.start_requests():
                if not isinstance(request, Request):
                    raise ValueError("start_requests 仅支持 yield Request")

                # 起始函数无 callback 默认添加
                if request.callback is None:
                    request.callback = self.parse

                self.queue.put(request)
        else:
            logger.warning("start_requests 函数不是生成器函数，将不会执行该函数！")

    def start_controller(self) -> None:
        """
        启动 controller

        :return:
        """
        # 启动相应数量的爬虫
        for _ in range(settings.REQUEST_THREADS):
            controller = SpiderController(q=self.queue, q_item=self.queue_item, spider=self)
            self.spider_controller_list.append(controller)
            controller.start()

        # 启动相应数量的item
        for _ in range(settings.ITEM_THREADS):
            controller = ItemController(q=self.queue_item, spider=self)
            self.item_controller_list.append(controller)
            controller.start()

    @abstractmethod
    def run(self) -> None:
        """
        程序启动入口

        :return:
        """

    @property
    def name(self) -> str:
        """
        获取 spider 的名字

        :return:
        """

        return self.__class__.spider_name or self.__class__.__name__

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


class Spider(SpiderBase):
    """
        外部引用：Spider 基类
    """

    def parse(self, request, response) -> None:
        """
        默认的解析函数（仅 start_requests 默认的）

        @result:
        """
        pass

    @abstractmethod
    def run(self) -> None:
        """
        程序启动入口

        :return:
        """

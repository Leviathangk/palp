"""
    分布式 spider
"""
import json
import time
import importlib
from palp import settings
from quickdb import RedisLock
from abc import abstractmethod
from palp.spider.spider import Spider
from palp.tool.client_heart import ClientHeart
from palp.tool.short_module import import_module
from palp.network.request import LoadRequest, Request
from palp.sequence.sequence_redis_item import FIFOItemRedisSequence
from palp.decorator.decorator_spider_wait import SpiderWaitDecorator
from palp.decorator.decorator_spider_once import SpiderOnceDecorator
from palp.decorator.decorator_run_func_by_thread import RunByThreadDecorator
from palp.sequence.sequence_redis_borrow import FIFORequestBorrowRedisSequence
from palp.decorator.decorator_spider_middleware import SpiderMiddlewareDecorator


class DistributiveSpider(Spider):
    """
        分布式 spider
    """

    def __new__(cls, *args, **kwargs):
        """
        加载 spider 设置，并定义 SPIDER_TYPE

        :param args:
        :param kwargs:
        """
        if not cls.SPIDER_MIDDLEWARE:
            setattr(settings, 'SPIDER_TYPE', 2)
            cls.from_settings()

        return object.__new__(cls)

    def __init__(self, thread_count=None, redis_key: str = None, request_filter=False, item_filter=False):
        """

        :param thread_count: 线程数量
        :param redis_key: 自定义 redis_key 的名字
        :param request_filter: 开启请求过滤，不然 filter_repeat 无效
        :param item_filter: 开启 item 过滤
        """
        self.spider_master = False
        self.redis_key = redis_key or self.name

        # 根据 spider 的名字设置 redis 前缀
        for key, value in settings.__dict__.items():
            if key.startswith('REDIS_KEY'):
                setattr(settings, key, value.format(redis_key=self.redis_key))

        super().__init__(thread_count, request_filter, item_filter)

        queue_module = settings.REQUEST_QUEUE[settings.SPIDER_TYPE][settings.REQUEST_QUEUE_MODE]
        self.queue = import_module(queue_module)[0]  # 请求队列
        self.queue_item = FIFOItemRedisSequence()  # item 队列
        self.queue_borrow = FIFORequestBorrowRedisSequence()  # 信息传递队列

    @abstractmethod
    def start_requests(self) -> None:
        """
        起始函数

        :return:
        """

    @staticmethod
    def start_check():
        """
        启动检查，防止上次意外结束，导致 master 死机 key 未删除，无法正常启动
        这里设定时间 10s 即出意外后，超过 10s 启动才会移除 master key

        :return:
        """
        from palp.conn import redis_conn

        master_detail = redis_conn.get(settings.REDIS_KEY_MASTER)
        if master_detail:
            master_detail = json.loads(master_detail.decode())
            heart_beat = redis_conn.hget(settings.REDIS_KEY_HEARTBEAT, master_detail['name'])

            # 没有心跳的情况下，master 创建时间不能与现在时间相差 5s 不然就有问题
            if not heart_beat:
                if time.time() - master_detail['time'] > 5:
                    redis_conn.delete(settings.REDIS_KEY_MASTER)

            # 有心跳的情况下，master 超过 10s 没有跳动，就是有问题
            elif time.time() - json.loads(heart_beat.decode())['time'] > 10:
                redis_conn.delete(settings.REDIS_KEY_MASTER)

    @RunByThreadDecorator(daemon=True)
    def start_distribute_failed_request(self):
        """
        重新放入 执行失败的请求任务

        :return:
        """
        from palp.conn import redis_conn

        if settings.REQUEST_RETRY_FAILED and redis_conn.exists(settings.REDIS_KEY_QUEUE_BAD_REQUEST):
            while True:
                request = redis_conn.spop(settings.REDIS_KEY_QUEUE_BAD_REQUEST, count=1)
                if not request:
                    break

                self.queue.put(LoadRequest.load_from_json(request[0].decode()))

    @RunByThreadDecorator(daemon=True)
    def start_distribute_failed_item(self) -> None:
        """
        重新放入 处理失败的 item

        :return:
        """
        from palp.conn import redis_conn

        modules = {}
        if settings.ITEM_RETRY_FAILED and redis_conn.exists(settings.REDIS_KEY_QUEUE_BAD_ITEM):
            while True:
                item = redis_conn.spop(settings.REDIS_KEY_QUEUE_BAD_ITEM, count=1)
                if not item:
                    break

                item = json.loads(item[0].decode())

                # 重新导入 item
                key = item['module'] + '.' + item['init']
                if key not in modules:
                    cls = importlib.import_module(item['module']).__getattribute__(item['init'])  # 导入
                    modules[key] = cls
                else:
                    cls = modules[key]

                self.queue_item.put(cls(**json.loads(item['data'])))

    def competition_for_master(self) -> None:
        """
        竞争为 master 并执行任务分配

        注意：任务分配为线程分配，不然数量一旦过多，将会影响程序执行

        :return:
        """
        from palp.conn import redis_conn

        with RedisLock(conn=redis_conn, lock_name=settings.REDIS_KEY_LOCK + 'Master', block_timeout=10):
            if redis_conn.exists(settings.REDIS_KEY_MASTER):
                return

            # 设置 master 标志
            self.spider_master = True
            redis_conn.set(settings.REDIS_KEY_MASTER, json.dumps({
                'name': self.spider_uuid,
                'time': time.time(),
            }, ensure_ascii=False))

            # 删除之前的锁
            keys = redis_conn.keys(settings.REDIS_KEY_LOCK + '*')
            if keys:
                remove_list = []

                for key in keys:
                    key = key.decode()
                    if key.endswith('Master'):
                        continue
                    remove_list.append(key)

                if remove_list:
                    redis_conn.delete(*remove_list)

            # 删除 cookie 池
            if settings.REQUEST_BORROW_DELETE_WHEN_START:
                redis_conn.delete(settings.REDIS_KEY_QUEUE_REQUEST_BORROW)

            # 删除停止标志、记录
            redis_conn.delete(settings.REDIS_KEY_STOP, settings.REDIS_KEY_RECORD)

            # 清空心跳
            redis_conn.delete(settings.REDIS_KEY_HEARTBEAT, settings.REDIS_KEY_HEARTBEAT_FAILED)

            # 分发失败的任务
            self.start_distribute_failed_request()
            self.start_distribute_failed_item()

            # 分发任务
            self.start_distribute()

    def borrow_request(self, request: Request):
        """
        开启 REQUEST_BORROW 时，用来主动使用资源

        :param request: 新的请求，决定何时调用
        :return:
        """
        from palp import conn

        if settings.REQUEST_BORROW and conn.redis_conn:

            # 空 cookie_jar 即视为新的请求，添加 cookie_jar
            if not request.cookie_jar and request.keep_cookie:
                recycle_data = self.queue_borrow.get()
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
        from palp import conn

        if settings.REQUEST_BORROW and conn.redis_conn:
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
        """
        分布式处理 逻辑

        :return:
        """
        from palp.conn import redis_conn

        self.start_controller()  # 任务处理
        self.start_check()  # 检查是否正常
        self.competition_for_master()  # 竞争为 master

        # 等待任务分发完毕，客户端无任务，视为执行结束
        ClientHeart(spider=self).start()

        # master 机器处理的事情
        if self.spider_master:
            # 删除 master、heart_failed 的标志
            redis_conn.delete(settings.REDIS_KEY_MASTER, settings.REDIS_KEY_HEARTBEAT_FAILED)
            # 判断是否移除 filter
            if not settings.PERSISTENCE_REQUEST_FILTER:
                redis_conn.delete(settings.REDIS_KEY_QUEUE_FILTER_REQUEST)
            if not settings.PERSISTENCE_ITEM_FILTER:
                redis_conn.delete(settings.REDIS_KEY_QUEUE_FILTER_ITEM)

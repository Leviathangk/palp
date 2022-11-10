"""
    分布式 spider
"""
import json
import time
from palp import settings
from threading import Thread
from abc import abstractmethod
from quickdb import RedisLockNoWait
from palp.buffer.buffer_item import ItemBuffer
from palp.spider.spider_base import BaseSpider
from palp.tool.client_heart import ClientHeart


class DistributiveSpider(BaseSpider, Thread):
    def __init__(self, thread_count=None, redis_key: str = None, request_filter=False, item_filter=False):
        """

        :param thread_count: 线程数量
        :param redis_key: 自定义 redis_key 的名字
        :param request_filter: 开启请求过滤，不然 filter_repeat 无效
        :param item_filter: 开启 item 过滤
        """
        setattr(settings, 'SPIDER_TYPE', 2)
        self.redis_key = redis_key or self.name

        # 根据 spider 的名字设置前缀
        setattr(settings, 'REDIS_KEY_QUEUE_ITEM', settings.REDIS_KEY_QUEUE_ITEM.format(redis_key=self.redis_key))
        setattr(settings, 'REDIS_KEY_MASTER', settings.REDIS_KEY_MASTER.format(redis_key=self.redis_key))
        setattr(settings, 'REDIS_KEY_STOP', settings.REDIS_KEY_STOP.format(redis_key=self.redis_key))
        setattr(settings, 'REDIS_KEY_LOCK', settings.REDIS_KEY_LOCK.format(redis_key=self.redis_key))
        setattr(settings, 'REDIS_KEY_HEARTBEAT', settings.REDIS_KEY_HEARTBEAT.format(redis_key=self.redis_key))
        setattr(settings, 'REDIS_KEY_QUEUE_REQUEST', settings.REDIS_KEY_QUEUE_REQUEST.format(redis_key=self.redis_key))

        setattr(settings, 'REDIS_KEY_HEARTBEAT_FAILED',
                settings.REDIS_KEY_HEARTBEAT_FAILED.format(redis_key=self.redis_key))
        setattr(settings, 'REDIS_KEY_QUEUE_FILTER_REQUEST',
                settings.REDIS_KEY_QUEUE_FILTER_REQUEST.format(redis_key=self.redis_key))
        setattr(settings, 'REDIS_KEY_QUEUE_FILTER_ITEM',
                settings.REDIS_KEY_QUEUE_FILTER_ITEM.format(redis_key=self.redis_key))

        super().__init__(thread_count, request_filter, item_filter)

    @abstractmethod
    def start_requests(self) -> None:
        """
        起始函数

        :return:
        """
        pass

    def parse(self, request, response) -> None:
        """
        解析

        :param request:
        :param response:
        :return:
        """
        pass

    def competition_for_master(self) -> None:
        """
        竞争为 master

        :return:
        """
        from palp.conn import redis_conn

        if redis_conn.exists(settings.REDIS_KEY_MASTER):
            return

        with RedisLockNoWait(conn=redis_conn, lock_name=settings.REDIS_KEY_LOCK) as lock:
            if lock.lock_success:
                self.spider_master = True
                redis_conn.set(settings.REDIS_KEY_MASTER, '')

    @staticmethod
    def start_check():
        """
        启动检查，防止上次意外结束，导致 master 死机 key 未删除，无法正常启动

        :return:
        """
        from palp.conn import redis_conn

        master_name = redis_conn.get(settings.REDIS_KEY_MASTER)
        if master_name:
            master_detail = redis_conn.hget(settings.REDIS_KEY_HEARTBEAT, master_name.decode())
            if master_detail and time.time() - json.loads(master_detail.decode())['time'] > 5:
                redis_conn.delete(settings.REDIS_KEY_MASTER)

    def spider_logic(self):
        """
        spider 处理逻辑

        :return:
        """
        from palp.conn import redis_conn

        # 检查是否正常
        self.start_check()

        # master 竞争
        self.competition_for_master()

        # master 机器处理的事情
        if self.spider_master:
            # 删除停止标志
            redis_conn.delete(settings.REDIS_KEY_STOP)
            # 清空心跳
            redis_conn.delete(settings.REDIS_KEY_HEARTBEAT, settings.REDIS_KEY_HEARTBEAT_FAILED)

            # 处理 item
            ItemBuffer.from_settings()
            self._item_buffer = ItemBuffer(spider=self, q=self._queue_item)
            self._item_buffer.start()

            # 分发任务
            self.distribute_task()
        else:
            time.sleep(1)  # 睡 1s 避免停止标志没被移除

        # 等待所有任务执行结束
        ClientHeart(spider=self).start()

        # master 机器处理的事情
        if self.spider_master:
            # 删除 master 的标志
            redis_conn.delete(settings.REDIS_KEY_MASTER)
            # 删除 stop 标志
            ClientHeart.remove_stop_status()
            # 判断是否移除 filter
            if not settings.PERSISTENCE_REQUEST_FILTER:
                redis_conn.delete(settings.REDIS_KEY_QUEUE_FILTER_REQUEST)
            if not settings.PERSISTENCE_ITEM_FILTER:
                redis_conn.delete(settings.REDIS_KEY_QUEUE_FILTER_ITEM)

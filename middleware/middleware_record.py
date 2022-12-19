"""
    请求记录中间件

    目前记录：
        请求数
        请求成功数
        请求失败数

    注意：
        双继承意味着双导入，所以不能在 init 上共享信息
        双继承的中间件，需要导入 2 次
        双继承的中间件，文件名、类名不含有 middleware_spider、middleware_request
"""
import json
import datetime
from typing import Union
from palp import settings
from palp.network.request import Request
from palp.decorator.decorator_lock import FuncLock
from palp.middleware.middleware_spider import SpiderMiddleware
from palp.middleware.middleware_request import RequestMiddleware


class RequestRecordMiddleware(RequestMiddleware, SpiderMiddleware):
    """
        请求记录中间件
    """
    request_count_all = 0  # 请求总数
    request_count_failed = 0  # 失败总数
    request_count_succeed = 0  # 成功总数

    @FuncLock()
    def request_in(self, spider, request) -> None:
        """
            记录进入的请求
        """
        self.__class__.request_count_all += 1

    @FuncLock()
    def request_failed(self, spider, request) -> None:
        """
            记录失败的请求
        """
        self.__class__.request_count_failed += 1

    @FuncLock()
    def request_close(self, spider, request, response) -> Union[Request, None]:
        """
            记录成功的请求
        """
        self.__class__.request_count_succeed += 1

        return

    def spider_close(self, spider) -> None:
        """
            直接双继承，通过 spider_close 上传记录信息
        """
        from palp.conn import redis_conn

        if settings.SPIDER_TYPE != 1:
            # 发送记录
            redis_conn.hset(settings.REDIS_KEY_RECORD, spider.spider_uuid, json.dumps({
                'request_all': self.__class__.request_count_all,
                'request_failed': self.__class__.request_count_failed,
                'request_succeed': self.__class__.request_count_succeed,
                'stop_time': str(datetime.datetime.now())
            }, ensure_ascii=False))

            # 删除心跳字段
            redis_conn.hdel(settings.REDIS_KEY_HEARTBEAT, spider.spider_uuid)

            # 如果是最后一个心跳，则进行统计记录
            if not redis_conn.exists(settings.REDIS_KEY_HEARTBEAT):
                request_all = 0
                request_failed = 0
                request_succeed = 0

                # 统计
                for spider_uuid, spider_detail in redis_conn.hgetall(settings.REDIS_KEY_RECORD).items():
                    spider_detail = json.loads(spider_detail.decode())

                    request_all += spider_detail['request_all']
                    request_failed += spider_detail['request_failed']
                    request_succeed += spider_detail['request_succeed']

                # 发送最后的统计结果
                redis_conn.set(settings.REDIS_KEY_STOP, json.dumps({
                    'request_all': request_all,
                    'request_failed': request_failed,
                    'request_succeed': request_succeed,
                    'stop_time': str(datetime.datetime.now())
                }, ensure_ascii=False))

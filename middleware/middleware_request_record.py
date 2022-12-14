"""
    请求记录中间件

    目前记录：
        请求数
        请求成功数
        请求失败数

    注意：双继承意味着双导入，所以不能在 init 上共享信息
"""
import json
from typing import Union
from palp import settings
from palp.network.request import Request
from palp.decorator.decorator_lock import FuncLock
from palp.middleware.middleware_spider import SpiderMiddleware
from palp.middleware.middleware_request import RequestMiddleware


class RequestsRecordMiddleware(RequestMiddleware, SpiderMiddleware):
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

        if redis_conn is not None:
            stop_time = redis_conn.get(settings.REDIS_KEY_STOP)
            redis_conn.set(settings.REDIS_KEY_STOP, json.dumps({
                'request_all': self.__class__.request_count_all,
                'request_failed': self.__class__.request_count_failed,
                'request_succeed': self.__class__.request_count_succeed,
                'stop_time': stop_time.decode()
            }, ensure_ascii=False))

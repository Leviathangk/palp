"""
    请求记录中间件

    目前记录：
        all：请求数
        succeed：请求成功数
        failed：请求失败数

    注意：
        通过引入 spider 自身的 spider_record 获取、修改对应信息
"""
import json
import datetime
from typing import Union
from palp import settings
from palp.network.request import Request
from palp.middleware.middleware_request import RequestMiddleware
from palp.decorator.decorator_lock import FuncLockSharedDecorator


class RequestRecordMiddleware(RequestMiddleware):
    """
        请求记录中间件
    """

    @FuncLockSharedDecorator(timeout=1)
    def request_in(self, spider, request) -> None:
        """
            记录进入的请求
        """
        spider.spider_record['all'] += 1

    @FuncLockSharedDecorator(timeout=1)
    def request_failed(self, spider, request) -> None:
        """
            记录失败的请求
        """
        spider.spider_record['failed'] += 1

    @FuncLockSharedDecorator(timeout=1)
    def request_close(self, spider, request, response) -> Union[Request, None]:
        """
            记录成功的请求
        """
        spider.spider_record['succeed'] += 1

        return

    def request_record(self, spider, record: dict) -> None:
        """
        发送总结果记录

        :param spider:
        :param record:
        :return:
        """
        from palp.conn import redis_conn

        if not redis_conn or settings.SPIDER_TYPE == 1:
            return

        record = {
            'all': record['all'],
            'failed': record['failed'],
            'succeed': record['succeed'],
            'stop_time': str(datetime.datetime.now())
        }

        redis_conn.set(settings.REDIS_KEY_STOP, json.dumps(record, ensure_ascii=False))

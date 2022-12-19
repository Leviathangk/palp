"""
    请求记录中间件

    目前记录：
        all：请求数
        succeed：请求成功数
        failed：请求失败数

    注意：
        通过引入 spider 自身的 spider_record 获取、修改对应信息
"""
from typing import Union
from palp.network.request import Request
from palp.decorator.decorator_lock import FuncLockDecorator
from palp.middleware.middleware_request import RequestMiddleware


class RequestRecordMiddleware(RequestMiddleware):
    """
        请求记录中间件
    """

    @FuncLockDecorator()
    def request_in(self, spider, request) -> None:
        """
            记录进入的请求
        """
        spider.spider_record['all'] += 1

    @FuncLockDecorator()
    def request_failed(self, spider, request) -> None:
        """
            记录失败的请求
        """
        spider.spider_record['failed'] += 1

    @FuncLockDecorator()
    def request_close(self, spider, request, response) -> Union[Request, None]:
        """
            记录成功的请求
        """
        spider.spider_record['succeed'] += 1

        return

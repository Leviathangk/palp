"""
    请求中间件
"""
from typing import Union
from palp.network.request import Request
from palp.network.response import Response
from palp.spider.spider import Spider


class RequestMiddlewareBase:
    """
        请求中间件基类
    """

    def request_in(self, spider: Spider, request: Request) -> None:
        """
        请求进入时的操作

        :param spider:
        :param request:
        :return:
        """

    def request_error(self, spider: Spider, request: Request, exception: Exception) -> Union[Request, None]:
        """
        请求出错时的操作

        :param spider:
        :param request: 该参数可返回（用于放弃当前请求，并发起新请求）
        :param exception: 错误
        :return: [Request, None]
        """

    def request_failed(self, spider: Spider, request: Request) -> None:
        """
        超过最大重试次数时的操作

        :param spider:
        :param request:
        :return:
        """

    def request_close(self, spider: Spider, request: Request, response: Response) -> Union[Request, None]:
        """
        请求结束时的操作

        :param spider:
        :param request: 该参数可返回（用于放弃当前请求，并发起新请求）
        :param response:
        :return: [Request, None]
        """

    def request_record(self, spider: Spider, record: dict) -> None:
        """
        发送请求记录，在 spider 执行完毕时，将会调用

        :param spider:
        :param record: {'all': 0, 'failed': 0, 'succeed': 0} 样式的字典
        :return:
        """


class RequestMiddleware(RequestMiddlewareBase):
    """
        外部引用：请求中间件
    """

    def request_in(self, spider, request) -> None:
        """
        请求进入时的操作

        :param spider:
        :param request:
        :return:
        """

    def request_error(self, spider, request, exception: Exception) -> Union[Request, None]:
        """
        请求出错时的操作

        :param spider:
        :param request: 该参数可返回（用于放弃当前请求，并发起新请求）
        :param exception: 错误
        :return: [Request, None]
        """

    def request_failed(self, spider, request) -> None:
        """
        超过最大重试次数时的操作

        :param spider:
        :param request:
        :return:
        """

    def request_close(self, spider, request, response) -> Union[Request, None]:
        """
        请求结束时的操作

        :param spider:
        :param request: 该参数可返回（用于放弃当前请求，并发起新请求）
        :param response:
        :return: [Request, None]
        """

    def request_record(self, spider, record: dict) -> None:
        """
        发送请求记录，在 spider 执行完毕时，将会调用

        :param spider:
        :param record: {'all': 0, 'failed': 0, 'succeed': 0} 样式的字典
        :return:
        """

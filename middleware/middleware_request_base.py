"""
    请求中间件
"""
from typing import Union
from loguru import logger
from palp.network.request import Request
from palp.network.response import Response
from palp.spider.spider_base import BaseSpider


class BaseRequestMiddleware:
    def request_in(self, spider: BaseSpider, request: Request) -> None:
        """
        请求进入时的操作

        :param spider:
        :param request:
        :return:
        """
        pass

    def request_close(self, spider: BaseSpider, request: Request, response: Response) -> Union[Request, None]:
        """
        请求结束时的操作

        :param spider:
        :param request: 该参数可返回（用于放弃当前请求，并发起新请求）
        :param response:
        :return: [Request, None]
        """
        return

    def request_error(self, spider: BaseSpider, request: Request, exception_type: str, exception: str) -> Union[
        Request, None]:
        """
        请求出错时的操作

        :param spider:
        :param request: 该参数可返回（用于放弃当前请求，并发起新请求）
        :param exception_type: 错误的类型
        :param exception: 错误的详细信息
        :return: [Request, None]
        """
        logger.error(exception)

        return

    def request_failed(self, spider: BaseSpider, request: Request) -> None:
        """
        超过最大重试次数时的操作

        :param spider:
        :param request:
        :return:
        """
        logger.warning(f"失败的请求：{request}")


# 用于外部引用，避免写类型
class RequestMiddleware(BaseRequestMiddleware):
    def request_in(self, spider, request) -> None:
        """
        请求进入时的操作

        :param spider:
        :param request:
        :return:
        """
        pass

    def request_close(self, spider, request, response):
        """
        请求结束时的操作

        :param spider:
        :param request: 该参数可返回（用于放弃当前请求，并发起新请求）
        :param response:
        :return: [Request, None]
        """
        return

    def request_error(self, spider, request, exception_type: str, exception: str):
        """
        请求出错时的操作

        :param spider:
        :param request: 该参数可返回（用于放弃当前请求，并发起新请求）
        :param exception_type: 错误的类型
        :param exception: 错误的详细信息
        :return: [Request, None]
        """

        return

    def request_failed(self, spider, request) -> None:
        """
        超过最大重试次数时的操作

        :param spider:
        :param request:
        :return:
        """
        pass
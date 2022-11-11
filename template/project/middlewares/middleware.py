"""
    中间件
    SpiderMiddleware：爬虫中间件
    RequestMiddleware：请求中间件

    参数全部可直接原地修改
"""
import palp
from loguru import logger


class SpiderMiddleware(palp.SpiderMiddleware):
    def spider_start(self, spider) -> None:
        """
        spider 开始时的操作

        :param spider:
        :return:
        """
        pass

    def spider_close(self, spider) -> None:
        """
        spider 结束的操作

        :param spider:
        :return:
        """
        pass

    def spider_error(self, spider, exception_type: str, exception: str) -> None:
        """
        spider 出错时的操作

        :param spider:
        :param exception_type: 错误的类型
        :param exception: 错误的详细信息
        :return:
        """
        logger.error(exception)


class RequestMiddleware(palp.RequestMiddleware):
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
        logger.error(exception)

        return

    def request_failed(self, spider, request) -> None:
        """
        超过最大重试次数时的操作

        :param spider:
        :param request:
        :return:
        """
        logger.warning(f"失败的请求：{request}")

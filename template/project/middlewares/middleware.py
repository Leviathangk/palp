"""
    Middleware

    注意：默认报错是 logger.error 输出，需要详细信息请使用 logger.exception（输出会很多，但很细）
"""
import palp
from typing import Union
from palp import settings
from loguru import logger
from palp.network.request import Request


class SpiderMiddleware(palp.SpiderMiddleware):
    """
        Spider 中间件：处理 spider 开启关闭任务
    """

    def spider_start(self, spider) -> None:
        """
        spider 开始时的操作

        :param spider:
        :return:
        """

    def spider_error(self, spider, exception: Exception) -> None:
        """
        spider 出错时的操作

        :param spider:
        :param exception: 错误的详细信息
        :return:
        """
        logger.error(exception)

    def spider_close(self, spider) -> None:
        """
        spider 结束的操作

        :param spider:
        :return:
        """


class RequestMiddleware(palp.RequestMiddleware):
    """
        Request 中间件：处理请求
    """

    def request_in(self, spider, request) -> None:
        """
        请求进入时的操作

        :param spider:
        :param request:
        :return:
        """
        if settings.REQUEST_PROXIES_TUNNEL_URL and not request.proxies:
            request.proxies = {
                'http': 'http://' + settings.REQUEST_PROXIES_TUNNEL_URL,
                'https': 'https://' + settings.REQUEST_PROXIES_TUNNEL_URL,
            }

    def request_error(self, spider, request, exception: Exception) -> Union[Request, None]:
        """
        请求出错时的操作

        :param spider:
        :param request: 该参数可返回（用于放弃当前请求，并发起新请求）
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

    def request_close(self, spider, request, response) -> Union[Request, None]:
        """
        请求结束时的操作

        :param spider:
        :param request: 该参数可返回（用于放弃当前请求，并发起新请求）
        :param response:
        :return: [Request, None]
        """
        return

    def request_record(self, spider, record: dict) -> None:
        """
        请求结果记录（在 spider 结束时调用）

        :param spider:
        :param record:
        :return:
        """
        logger.info("{} 执行完毕，请求量统计：{}", spider.spider_name, record)

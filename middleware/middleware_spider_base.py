"""
    spider 中间件
"""
from loguru import logger
from palp.spider.spider_base import BaseSpider


class BaseSpiderMiddleware:
    def spider_start(self, spider: BaseSpider) -> None:
        """
        spider 开始时的操作

        :param spider:
        :return:
        """
        pass

    def spider_close(self, spider: BaseSpider) -> None:
        """
        spider 结束的操作

        :param spider:
        :return:
        """
        pass

    def spider_error(self, spider: BaseSpider, exception_type: str, exception: str) -> None:
        """
        spider 出错时的操作

        :param spider:
        :param exception_type: 错误的类型
        :param exception: 错误的详细信息
        :return:
        """

        logger.error(exception)


# 用于外部引用，避免写类型
class SpiderMiddleware(BaseSpiderMiddleware):
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

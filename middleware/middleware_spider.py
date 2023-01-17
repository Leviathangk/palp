"""
    spider 中间件
"""
from palp.spider.spider import Spider


class SpiderBaseMiddleware:
    """
        spider 中间件基类
    """

    def spider_start(self, spider: Spider) -> None:
        """
        spider 开始时的操作

        :param spider:
        :return:
        """

    def spider_error(self, spider: Spider, exception: Exception) -> None:
        """
        spider 出错时的操作

        :param spider:
        :param exception: 错误
        :return:
        """

    def spider_close(self, spider: Spider) -> None:
        """
        spider 结束的操作

        :param spider:
        :return:
        """

    def spider_end(self, spider: Spider) -> None:
        """
        spider 结束的操作（分布式时多个机器也只会执行一次）

        :param spider:
        :return:
        """


class SpiderMiddleware(SpiderBaseMiddleware):
    """
        外部引用：请求中间件
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
        :param exception: 错误
        :return:
        """

    def spider_close(self, spider) -> None:
        """
        spider 结束的操作

        :param spider:
        :return:
        """

    def spider_end(self, spider) -> None:
        """
        spider 结束的操作（分布式时多个机器也只会执行一次）

        :param spider:
        :return:
        """

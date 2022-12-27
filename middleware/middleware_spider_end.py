"""
    spider 结束中间件，最后一个运行

    仅用作提示
"""
from loguru import logger
from palp.middleware.middleware_spider import SpiderMiddleware


class SpiderEndMiddleware(SpiderMiddleware):
    """
        spider 资源回收中间件
    """

    def spider_close(self, spider):
        """
        关闭所有创建的连接

        :param spider:
        :return:
        """
        logger.debug("爬虫已停止")

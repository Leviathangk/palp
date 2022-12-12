"""
    等待 spider 各项功能执行结束
"""
from palp.middleware.middleware_spider import SpiderMiddleware


class SpiderWaitMiddleware(SpiderMiddleware):
    """
        等待功能执行结束
    """

    def spider_close(self, spider):
        """
        等待 spider controller、item controller 执行完毕
        :param spider:
        :return:
        """
        spider.wait_spider_controller_done()
        spider.wait_item_controller_done()

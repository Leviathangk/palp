"""
    周期爬虫记录请求中间件

    注意：
        双继承的中间件，需要导入 2 次
        双继承的中间件，文件名、类名不含有 middleware_spider、middleware_request
"""
import datetime
from palp import settings
from palp.spider.spider_cycle import CycleSpider
from palp.middleware.middleware_spider import SpiderMiddleware
from palp.middleware.middleware_request import RequestMiddleware


class CycleSpiderRecordRequestMiddleware(RequestMiddleware, SpiderMiddleware):
    """
        周期爬虫记录请求中间件
    """

    def spider_start(self, spider) -> None:
        self.start_time = datetime.datetime.now()

    def request_failed(self, spider, request):
        """
        失败请求记录

        :param spider:
        :param request:
        :return:
        """
        if issubclass(spider, CycleSpider) and hasattr(request, 'task'):
            spider.set_task_state_failed(task_id=request.task['id'])

    def request_close(self, spider, request, response):
        """
        成功请求记录

        :param spider:
        :param request:
        :return:
        """
        if issubclass(spider, CycleSpider) and hasattr(request, 'task'):
            spider.set_task_state_done(task_id=request.task['id'])

    def spider_close(self, spider) -> None:
        """
        写入记录表

        :param spider:
        :return:
        """
        from palp.conn import redis_conn

        if settings.SPIDER_TYPE == 1:
            pass
        else:
            pass

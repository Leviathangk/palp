"""
    周期爬虫记录请求中间件

    注意：
        双继承的中间件，需要导入 2 次
        双继承的中间件，文件名、类名不含有 middleware_spider、middleware_request
"""
from palp.spider.spider_cycle import CycleSpider
from palp.middleware.middleware_spider import SpiderMiddleware
from palp.middleware.middleware_request import RequestMiddleware


class CycleSpiderRecordRequestMiddleware(RequestMiddleware, SpiderMiddleware):
    """
        周期爬虫记录请求中间件
    """

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

        :param spider:
        :return:
        """

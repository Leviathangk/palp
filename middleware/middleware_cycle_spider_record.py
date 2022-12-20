"""
    周期爬虫记录请求中间件

    注意：
        双继承的中间件，需要导入 2 次
        双继承的中间件，文件名、类名不含有 middleware_spider、middleware_request
"""
import json
from palp import settings
from quickdb import RedisLock
from palp.spider.spider import Spider
from palp.spider.spider_cycle import CycleSpider
from palp.middleware.middleware_spider import SpiderMiddleware
from palp.middleware.middleware_request import RequestMiddleware


class CycleSpiderRecordMiddleware(RequestMiddleware, SpiderMiddleware):
    """
        周期爬虫记录请求中间件
    """

    def spider_start(self, spider) -> None:
        """
        周期爬虫，启动插入初始记录

        :param spider:
        :return:
        """
        from palp.conn import redis_conn

        if not issubclass(spider, CycleSpider) and not issubclass(spider, Spider):
            return

        with RedisLock(conn=redis_conn, lock_name=settings.REDIS_KEY_LOCK + 'CycleSpiderRecord'):
            if not redis_conn.exists(settings.REDIS_KEY_UUID):
                redis_conn.set(settings.REDIS_KEY_UUID, spider.spider_uuid)
                spider.insert_task_record_start(uuid=spider.spider_uuid)

    def request_failed(self, spider, request):
        """
        失败请求记录

        :param spider:
        :param request:
        :return:
        """
        if issubclass(spider, CycleSpider) and not issubclass(spider, Spider) and hasattr(request, 'task_id'):
            spider.set_task_state_failed(task_id=request.task_id)

    def request_close(self, spider, request, response):
        """
        成功请求记录

        :param spider:
        :param request:
        :return:
        """
        if issubclass(spider, CycleSpider) and not issubclass(spider, Spider) and hasattr(request, 'task_id'):
            spider.set_task_state_done(task_id=request.task_id)

    def spider_close(self, spider) -> None:
        """
        写入记录表

        :param spider:
        :return:
        """
        from palp.conn import redis_conn

        if not issubclass(spider, CycleSpider) and not issubclass(spider, Spider):
            return

        if settings.SPIDER_TYPE == 1:
            record = spider.spider_record
            spider.update_task_record(total=record['total'], succeed=record['succeed'], failed=record['failed'])
            spider.update_task_record_end()
        else:
            if not redis_conn.exists(settings.REDIS_KEY_HEARTBEAT):
                uuid = redis_conn.get(settings.REDIS_KEY_UUID)
                record = json.loads(redis_conn.get(settings.REDIS_KEY_STOP).decode())
                spider.update_task_record(
                    total=record['total'],
                    succeed=record['succeed'],
                    failed=record['failed'],
                    uuid=uuid
                )
                spider.update_task_record_end(uuid=uuid)

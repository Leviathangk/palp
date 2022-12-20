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

        # 判断是否是 CycleSpider 并继承了其它 spider（没写一行是为了避免导入后被其它爬虫误用）
        if not isinstance(spider, CycleSpider):
            return
        if not issubclass(spider.__class__, Spider):
            return

        if settings.SPIDER_TYPE == 1:
            spider.insert_task_record_start()
        else:
            with RedisLock(conn=redis_conn, lock_name=settings.REDIS_KEY_LOCK + 'CycleSpiderRecord'):
                if self.check_max_id_is_done(spider=spider):
                    spider.insert_task_record_start()

    def request_failed(self, spider, request):
        """
        失败请求记录

        :param spider:
        :param request:
        :return:
        """
        if not isinstance(spider, CycleSpider):
            return
        if not issubclass(spider.__class__, Spider):
            return

        if hasattr(request, 'task_id'):
            spider.set_task_state_failed(task_id=request.task_id)

    def request_close(self, spider, request, response):
        """
        成功请求记录

        :param spider:
        :param request:
        :return:
        """
        if not isinstance(spider, CycleSpider):
            return
        if not issubclass(spider.__class__, Spider):
            return

        if hasattr(request, 'task_id'):
            spider.set_task_state_done(task_id=request.task_id)

    def spider_close(self, spider) -> None:
        """
        写入记录表

        :param spider:
        :return:
        """
        from palp.conn import redis_conn

        if not isinstance(spider, CycleSpider):
            return
        if not issubclass(spider.__class__, Spider):
            return

        if settings.SPIDER_TYPE == 1:
            record = spider.spider_record
            spider.update_task_record(
                total=record['all'],
                succeed=record['succeed'],
                failed=record['failed'],
            )
            spider.update_task_record_end()
        else:
            if not redis_conn.exists(settings.REDIS_KEY_HEARTBEAT):
                try:
                    record = json.loads(redis_conn.get(settings.REDIS_KEY_STOP).decode())
                    spider.update_task_record(
                        total=record['all'],
                        succeed=record['succeed'],
                        failed=record['failed'],
                    )
                finally:
                    spider.update_task_record_end()

    @classmethod
    def check_max_id_is_done(cls, spider: CycleSpider) -> bool:
        """
        检查最大 id 的执行状态

        :param spider: spider
        :return:
        """
        from palp.conn import mysql_conn

        sql = f'''
            SELECT
                max( id ),
                is_done
            FROM
                `{spider.spider_table_record_name}`
        '''

        res = mysql_conn.execute(sql=sql, fetchone=True)

        if res[-1] is None:
            return True
        else:
            return bool(res[-1])

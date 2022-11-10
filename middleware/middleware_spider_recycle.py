"""
    spider 资源回收中间件
"""
from palp import conn
from palp.middleware.middleware_spider_base import BaseSpiderMiddleware


class SpiderRecycleMiddleware(BaseSpiderMiddleware):
    def spider_close(self, spider) -> None:
        """
        关闭所有创建的连接

        :param spider:
        :return:
        """
        if conn.redis_conn:
            conn.redis_conn.close()
        if conn.pg_conn:
            conn.pg_conn.engine.dispose()
        if conn.mysql_conn:
            conn.mysql_conn.engine.dispose()
        if conn.mongo_conn:
            conn.mongo_conn.close()
        if conn.kafka_conn:
            conn.kafka_conn.close()

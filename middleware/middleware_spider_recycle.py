"""
    spider 资源回收中间件
"""
from palp import conn
from palp.middleware.middleware_spider import SpiderMiddleware


class SpiderRecycleMiddleware(SpiderMiddleware):
    """
        spider 资源回收中间件
    """

    def spider_close(self, spider):
        """
        关闭所有创建的连接

        :param spider:
        :return:
        """
        # 关闭 redis
        try:
            if conn.redis_conn:
                conn.redis_conn.close()
        except:
            pass

        # 关闭 pg 连接
        try:
            if conn.pg_conn:
                conn.pg_conn.close_all()
        except:
            pass

        # 关闭 mysql 连接
        try:
            if conn.mysql_conn:
                conn.mysql_conn.close_all()
        except:
            pass

        # 关闭 mongo 连接
        try:
            if conn.mongo_conn:
                conn.mongo_conn.close()
        except:
            pass

        # 关闭 kafka 连接
        try:
            if conn.kafka_conn:
                conn.kafka_conn.close()
        except:
            pass

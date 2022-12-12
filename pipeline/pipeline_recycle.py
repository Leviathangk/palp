"""
    item 失败回收中间件
"""
import json
from palp import settings
from palp.pipeline.pipeline import Pipeline


class RedisRecyclePipeline(Pipeline):
    """
        对重试多次失败的 item 进行回收，放入 redis 失败队列
    """

    def pipeline_failed(self, spider, item) -> None:
        """
        回收失败的 item

        :param spider:
        :param item:
        :return:
        """
        from palp.conn import redis_conn

        if redis_conn is None:
            return

        redis_conn.sadd(settings.REDIS_KEY_QUEUE_BAD_ITEM, json.dumps({
            'module': item.__class__.__module__,  # 引用自哪里
            'init': item.__class__.__name__,  # 引用的模块名
            'data': item.to_json()
        }))

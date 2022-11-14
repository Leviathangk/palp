"""
    item 失败回收中间件
"""
import json
from palp import settings
from palp.pipeline.pipeline_base import Pipeline


class ItemRecyclePipeline(Pipeline):
    def pipeline_failed(self, spider, item) -> None:
        """
        对重试多次失败的 item 进行回收

        :param spider:
        :param item:
        :return:
        """
        from palp.conn import redis_conn

        redis_conn.sadd(settings.REDIS_KEY_QUEUE_BAD_ITEM, json.dumps({
            'module': item.__class__.__module__,  # 引用自哪里
            'init': item.__class__.__name__,  # 引用的模块名
            'data': item.to_json()
        }))

"""
    redis 队列
    使用了 pickle 并使用 zlib 压缩
"""
import zlib
import pickle
from palp import settings
from palp.conn import redis_conn
from palp.sequence.sequence_base import BaseSequence


# 先进先出队列
class FIFOSequence(BaseSequence):
    def __init__(self):
        super().__init__()

    def put(self, obj, timeout: int = None):
        """
        添加任务

        :param obj:
        :param timeout:
        :return:
        """
        redis_conn.rpush(settings.REDIS_KEY_QUEUE_ITEM, zlib.compress(pickle.dumps(obj)))

    def get(self, timeout: int = None):
        """
        获取任务（这里是返回的对象）

        :return:
        """
        result = redis_conn.blpop(settings.REDIS_KEY_QUEUE_ITEM, timeout=timeout)
        if result:
            return pickle.loads(zlib.decompress(result[-1]))  # 这里不需要 decode 因为是对象

    def empty(self):
        """
        判断队列是否为空

        :return:
        """
        return redis_conn.llen(settings.REDIS_KEY_QUEUE_ITEM) == 0

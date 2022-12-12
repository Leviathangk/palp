"""
    redis item 队列
    使用了 pickle 并使用 zlib 压缩
"""
from palp import settings
from palp.sequence.sequence_redis_request import FIFORequestRedisSequence, LIFORequestRedisSequence


class FIFOItemRedisSequence(FIFORequestRedisSequence):
    """
        先进先出队列
    """

    @classmethod
    def get_redis_key(cls):
        """
        获取 redis 的键

        :return:
        """
        return settings.REDIS_KEY_QUEUE_ITEM


class LIFOItemRedisSequence(LIFORequestRedisSequence, FIFOItemRedisSequence):
    """
        后进先出队列
    """

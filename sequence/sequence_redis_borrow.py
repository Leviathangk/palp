"""
    redis borrow 队列
    使用了 pickle 并使用 zlib 压缩
"""
import zlib
import pickle
from palp import settings
from palp.sequence.sequence import RedisSequence


class FIFORequestBorrowRedisSequence(RedisSequence):
    """
        先进先出队列
    """

    @classmethod
    def get_redis_key(cls):
        """
        获取 redis 的键

        :return:
        """
        return settings.REDIS_KEY_QUEUE_REQUEST_BORROW

    def put(self, obj, timeout=None, **kwargs):
        """
        添加任务

        :param obj:
        :param timeout:
        :return:
        """
        from palp.conn import redis_conn

        redis_conn.rpush(self.redis_key, zlib.compress(pickle.dumps(obj)))

    def get(self, timeout=None, **kwargs):
        """
        获取任务（这里是返回的对象）

        :return:
        """
        from palp.conn import redis_conn

        result = redis_conn.lpop(self.redis_key)  # 这里就不能阻塞了
        if result:
            return pickle.loads(zlib.decompress(result))

    def empty(self):
        """
        判断队列是否为空

        :return:
        """
        from palp.conn import redis_conn

        return redis_conn.llen(self.redis_key) == 0

    def qsize(self):
        """
        返回队列大小

        :return:
        """
        from palp.conn import redis_conn

        return redis_conn.llen(self.redis_key)

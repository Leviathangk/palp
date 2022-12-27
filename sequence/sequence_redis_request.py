"""
    redis request 队列
"""
from palp import settings
from palp.network.request import LoadRequest
from palp.sequence.sequence import RedisSequence


class FIFORequestRedisSequence(RedisSequence):
    """
        先进先出队列
    """

    @classmethod
    def get_redis_key(cls):
        """
        获取 redis 的键

        :return:
        """
        return settings.REDIS_KEY_QUEUE_REQUEST

    def put(self, obj, timeout=None):
        """
        添加任务

        :param obj:
        :param timeout:
        :return:
        """
        from palp.conn import redis_conn

        redis_conn.rpush(self.redis_key, obj.to_json())

    def get(self, timeout=None):
        """
        获取任务（这里是返回的对象）

        :return:
        """
        from palp.conn import redis_conn

        result = redis_conn.blpop(self.redis_key, timeout=timeout)
        if result:
            return LoadRequest.load_from_json(result[-1].decode())

    def empty(self):
        """
        判断队列是否为空

        :return:
        """
        from palp.conn import redis_conn

        return redis_conn.llen(self.redis_key) == 0


class LIFORequestRedisSequence(FIFORequestRedisSequence):
    """
        后进先出队列
    """

    def get(self, timeout=None):
        """
        获取任务
        :return:
        """
        from palp.conn import redis_conn

        result = redis_conn.brpop(self.redis_key, timeout=timeout)
        if result:
            return LoadRequest.load_from_json(result[-1].decode())

class PriorityRequestRedisSequence(FIFORequestRedisSequence):
    """
        优先级队列
    """

    def put(self, obj, timeout=None):
        """
        添加任务

        :param obj:
        :param timeout:
        :return:
        """
        from palp.conn import redis_conn

        redis_conn.zadd(self.redis_key, {obj.to_json(): obj.priority})

    def get(self, timeout=None):
        """
        获取任务（这里是返回的对象）

        :return:
        """
        from palp.conn import redis_conn

        result = redis_conn.bzpopmin(self.redis_key, timeout=timeout)
        if result:
            return LoadRequest.load_from_json(result[1].decode())

    def empty(self):
        """
        判断队列是否为空

        :return:
        """
        from palp.conn import redis_conn

        return redis_conn.zcard(self.redis_key) == 0

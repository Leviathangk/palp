"""
    redis set 过滤

    print(BloomFilter.is_repeat(request=RequestGet(url='https://www.baidu.com')))
    print(BloomFilter.is_repeat(request=RequestGet(url='https://www.baidu.com')))
"""

from palp import settings
from quickdb import RedisLock
from palp.network.request import Request
from palp.filter.filter_base import BaseFilter


class RequestRedisFilter(BaseFilter):

    def is_repeat(self, obj, **kwargs) -> bool:
        """
        获取对应的指纹，通过 redis 的 set 去重

        :param obj:
        :param kwargs:
        :return:
        """
        from palp.conn import redis_conn

        fingerprint = self.fingerprint(obj=obj)

        if isinstance(obj, Request):
            redis_key_filter = settings.REDIS_KEY_QUEUE_FILTER_REQUEST
        else:
            redis_key_filter = settings.REDIS_KEY_QUEUE_FILTER_ITEM

        if settings.STRICT_FILTER:
            with RedisLock(conn=redis_conn, lock_name=settings.REDIS_KEY_LOCK):
                return self.judge(fingerprint, redis_key_filter)
        else:
            return self.judge(fingerprint, redis_key_filter)

    def judge(self, fingerprint, f) -> bool:
        """
        进行判断

        :param fingerprint:
        :param f:
        :return:
        """
        from palp.conn import redis_conn

        if redis_conn.sismember(f, fingerprint):
            return True

        redis_conn.sadd(f, fingerprint)

        return False

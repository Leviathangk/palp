"""
    redis set 过滤

    print(BloomFilter.is_repeat(request=RequestGet(url='https://www.baidu.com')))
    print(BloomFilter.is_repeat(request=RequestGet(url='https://www.baidu.com')))
"""
from palp import settings
from palp.network.request import Request
from palp.filter.filter_base import BaseFilter
from palp.conn.conn_redis import Redis, RedisLock


class RequestRedisFilter(BaseFilter):

    def is_repeat(self, obj, **kwargs) -> bool:
        """
        获取对应的指纹，通过 redis 的 set 去重

        :param obj:
        :param kwargs:
        :return:
        """
        fingerprint_md5 = self.fingerprint(obj=obj)

        if isinstance(obj, Request):
            redis_key_filter = settings.REDIS_KEY_QUEUE_FILTER_REQUEST
        else:
            redis_key_filter = settings.REDIS_KEY_QUEUE_FILTER_ITEM

        with RedisLock(lock_name=settings.REDIS_KEY_LOCK):
            if Redis.conn().sismember(redis_key_filter, fingerprint_md5):
                return True

            Redis.conn().sadd(redis_key_filter, fingerprint_md5)

            return False

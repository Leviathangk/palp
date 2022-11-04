"""
    redis 上才布隆过滤器
    学习链接：https://cuiqingcai.com/8472.html
"""
from palp import settings
from palp.network.request import Request
from palp.filter.filter_base import BaseFilter
from palp.conn.conn_redis import Redis, RedisLock


class RequestRedisBloomFilter(BaseFilter):
    def __init__(self):
        """
        Initialize BloomFilter

        """
        self.m = 1 << settings.BLOOMFILTER_BIT
        self.seeds = range(settings.BLOOMFILTER_HASH_NUMBER)

    def is_repeat(self, obj, **kwargs) -> bool:
        """
        获取对应的指纹，通过本地实现 redis 的 布隆过滤器 去重

        :param obj:
        :param kwargs:
        :return:
        """

        fingerprint = self.fingerprint(obj)

        if isinstance(obj, Request):
            redis_key_filter = settings.REDIS_KEY_QUEUE_FILTER_REQUEST
        else:
            redis_key_filter = settings.REDIS_KEY_QUEUE_FILTER_ITEM

        with RedisLock(lock_name=settings.REDIS_KEY_LOCK):
            if self.exists(fingerprint=fingerprint, redis_key_filter=redis_key_filter):
                return True

            self.insert(fingerprint=fingerprint, redis_key_filter=redis_key_filter)

            return False

    def exists(self, fingerprint: str, redis_key_filter: str):
        """
        判断值是否存在

        :return:
        """
        if not fingerprint:
            return False
        exist = 1
        for seed in self.seeds:
            offset = self.hash(seed, fingerprint)
            exist = exist & Redis.conn().getbit(redis_key_filter, offset)
        return exist

    def insert(self, fingerprint: str, redis_key_filter: str):
        """
        把值加入到 bloom

        :return:
        """
        for seed in self.seeds:
            offset = self.hash(seed, fingerprint)
            Redis.conn().setbit(redis_key_filter, offset, 1)

    def hash(self, seed: int, value: str):
        """
        Hash

        :return:
        """
        ret = 0
        for i in range(len(value)):
            ret += seed * ret + ord(value[i])
        return (self.m - 1) & ret

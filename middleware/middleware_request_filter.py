"""
    request 去重

    注意：
        setting 启用才会去重
        只有设置 filter_repeat 才会对请求做 阻拦 操作
"""
from palp import settings
from palp.filter.filter_bloom import BloomFilter
from palp.filter.filter_redis_set import RedisSetFilter
from palp.filter.filter_set import SetFilter
from palp.exception import DropRequestException
from palp.filter.filter_redis_bloom import RedisBloomFilter
from palp.middleware.middleware_request import RequestMiddleware


class SetFilterMiddleware(RequestMiddleware):
    """
        基于内存的 set 的去重
    """

    def __init__(self):
        self.request_memory_filter = SetFilter()

    def request_in(self, spider, request):
        if settings.FILTER_REQUEST:
            is_repeat = self.request_memory_filter.is_repeat(obj=request)

            if request.filter_repeat and is_repeat:
                raise DropRequestException(f"丢弃重复请求：{request}")


class BloomFilterMiddleware(RequestMiddleware):
    """
        基于内存的 bloom 的去重
    """

    def __init__(self):
        self.request_bloom_filter = BloomFilter()

    def request_in(self, spider, request):
        if settings.FILTER_REQUEST:
            is_repeat = self.request_bloom_filter.is_repeat(obj=request)

            if request.filter_repeat and is_repeat:
                raise DropRequestException(f"丢弃重复请求：{request}")


class RedisSetFilterMiddleware(RequestMiddleware):
    """
        基于 redis 的 set 的去重
    """

    def __init__(self):
        self.request_redis_filter = RedisSetFilter()

    def request_in(self, spider, request):
        if settings.FILTER_REQUEST:
            is_repeat = self.request_redis_filter.is_repeat(obj=request)

            if request.filter_repeat and is_repeat:
                raise DropRequestException(f"丢弃重复请求：{request}")


class RedisBloomFilterMiddleware(RequestMiddleware):
    """
        基于 redis 的 bloom 去重
    """

    def __init__(self):
        self.request_redis_bloom_filter = RedisBloomFilter()

    def request_in(self, spider, request):
        if settings.FILTER_REQUEST:
            is_repeat = self.request_redis_bloom_filter.is_repeat(obj=request)

            if request.filter_repeat and is_repeat:
                raise DropRequestException(f"丢弃重复请求：{request}")

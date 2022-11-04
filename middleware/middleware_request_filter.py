"""
    request 去重

    setting 启用才会去重
    请求过来不论设置不设置 filter_repeat 都会加入去重
    只有设置 filter_repeat 才会对请求做 阻拦 操作
"""
from palp import settings
from palp.filter.filter_bloom import BloomFilter
from palp.filter.filter_redis import RequestRedisFilter
from palp.filter.filter_memory import RequestMemoryFilter
from palp.exception.exception_drop import DropRequestException
from palp.filter.filter_redis_bloom import RequestRedisBloomFilter
from palp.middleware.middleware_request_base import BaseRequestMiddleware


# 本地：基于 python set 的去重
class RequestMemoryFilterMiddleware(BaseRequestMiddleware):
    def __init__(self):
        self.request_memory_filter = RequestMemoryFilter()

    def request_in(self, spider, request) -> None:
        if settings.REQUEST_FILTER:
            is_repeat = self.request_memory_filter.is_repeat(obj=request)

            if request.filter_repeat and is_repeat:
                raise DropRequestException(f"丢弃重复请求：{request}")


# 本地：基于 bloom 的去重
class RequestBloomFilterMiddleware(BaseRequestMiddleware):
    def __init__(self):
        self.request_bloom_filter = BloomFilter()

    def request_in(self, spider, request) -> None:
        if settings.REQUEST_FILTER:
            is_repeat = self.request_bloom_filter.is_repeat(obj=request)

            if request.filter_repeat and is_repeat:
                raise DropRequestException(f"丢弃重复请求：{request}")


# redis：基于 redis set 的去重
class RequestRedisFilterMiddleware(BaseRequestMiddleware):
    def __init__(self):
        self.request_redis_filter = RequestRedisFilter()

    def request_in(self, spider, request) -> None:
        if settings.REQUEST_FILTER:
            is_repeat = self.request_redis_filter.is_repeat(obj=request)

            if request.filter_repeat and is_repeat:
                raise DropRequestException(f"丢弃重复请求：{request}")


# redis：基于 redis 的 bloom 去重
class RequestRedisBloomFilterMiddleware(BaseRequestMiddleware):
    def __init__(self):
        self.request_redis_bloom_filter = RequestRedisBloomFilter()

    def request_in(self, spider, request) -> None:
        if settings.REQUEST_FILTER:
            is_repeat = self.request_redis_bloom_filter.is_repeat(obj=request)

            if request.filter_repeat and is_repeat:
                raise DropRequestException(f"丢弃重复请求：{request}")

"""
    item 去重

    setting 启用才会去重，但是会提前存指纹
"""
from palp import settings
from palp.filter.filter_bloom import BloomFilter
from palp.pipeline.pipeline_base import BasePipeline
from palp.filter.filter_redis import RequestRedisFilter
from palp.filter.filter_memory import RequestMemoryFilter
from palp.exception.exception_drop import DropItemException
from palp.filter.filter_redis_bloom import RequestRedisBloomFilter


# 本地：基于 python set 的去重
class ItemMemoryFilterPipeline(BasePipeline):
    def __init__(self):
        self.item_memory_filter = RequestMemoryFilter()

    def pipeline_in(self, spider, item) -> None:
        if settings.ITEM_FILTER:
            is_repeat = self.item_memory_filter.is_repeat(spider=spider, obj=item)

            if is_repeat:
                raise DropItemException(f"丢弃重复 item：{item}")


# 本地：基于 bloom 的去重
class ItemBloomFilterPipeline(BasePipeline):
    def __init__(self):
        self.item_bloom_filter = BloomFilter()

    def pipeline_in(self, spider, item) -> None:
        if settings.ITEM_FILTER:
            is_repeat = self.item_bloom_filter.is_repeat(spider=spider, obj=item)

            if is_repeat:
                raise DropItemException(f"丢弃重复 item：{item}")


# redis：基于 redis set 的去重
class ItemRedisFilterPipeline(BasePipeline):
    def __init__(self):
        self.item_redis_filter = RequestRedisFilter()

    def pipeline_in(self, spider, item) -> None:
        if settings.ITEM_FILTER:
            is_repeat = self.item_redis_filter.is_repeat(spider=spider, obj=item)

            if is_repeat:
                raise DropItemException(f"丢弃重复 item：{item}")


# redis：基于 redis 的 bloom 去重
class ItemRedisBloomFilterPipeline(BasePipeline):
    def __init__(self):
        self.item_redis_bloom_filter = RequestRedisBloomFilter()

    def pipeline_in(self, spider, item) -> None:
        if settings.ITEM_FILTER:
            is_repeat = self.item_redis_bloom_filter.is_repeat(spider=spider, obj=item)

            if is_repeat:
                raise DropItemException(f"丢弃重复 item：{item}")

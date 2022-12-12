"""
    item 去重

    注意：
        setting 启用才会去重
"""
from palp import settings
from palp.filter.filter_bloom import BloomFilter
from palp.pipeline.pipeline import Pipeline
from palp.filter.filter_redis_set import RedisSetFilter
from palp.filter.filter_set import SetFilter
from palp.exception import DropItemException
from palp.filter.filter_redis_bloom import RedisBloomFilter


class SetFilterPipeline(Pipeline):
    """
        基于内存的 set 的去重
    """

    def __init__(self):
        self.item_memory_filter = SetFilter()

    def pipeline_in(self, spider, item):
        if settings.FILTER_ITEM:
            is_repeat = self.item_memory_filter.is_repeat(spider=spider, obj=item)

            if is_repeat:
                raise DropItemException(f"丢弃重复 item：{item}")


class BloomFilterPipeline(Pipeline):
    """
        基于内存的 bloom 的去重
    """

    def __init__(self):
        self.item_bloom_filter = BloomFilter()

    def pipeline_in(self, spider, item):
        if settings.FILTER_ITEM:
            is_repeat = self.item_bloom_filter.is_repeat(spider=spider, obj=item)

            if is_repeat:
                raise DropItemException(f"丢弃重复 item：{item}")


class RedisSetFilterPipeline(Pipeline):
    """
        基于 redis 的 set 的去重
    """

    def __init__(self):
        self.item_redis_filter = RedisSetFilter()

    def pipeline_in(self, spider, item):
        if settings.FILTER_ITEM:
            is_repeat = self.item_redis_filter.is_repeat(spider=spider, obj=item)

            if is_repeat:
                raise DropItemException(f"丢弃重复 item：{item}")


class RedisBloomFilterPipeline(Pipeline):
    """
        基于 redis 的 bloom 去重
    """

    def __init__(self):
        self.item_redis_bloom_filter = RedisBloomFilter()

    def pipeline_in(self, spider, item):
        if settings.FILTER_ITEM:
            is_repeat = self.item_redis_bloom_filter.is_repeat(spider=spider, obj=item)

            if is_repeat:
                raise DropItemException(f"丢弃重复 item：{item}")

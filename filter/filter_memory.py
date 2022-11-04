"""
    本地内存去重

    print(MemoryFilter.is_repeat(request=RequestGet(url='https://www.baidu.com')))
    print(MemoryFilter.is_repeat(request=RequestGet(url='https://www.baidu.com')))
"""
from palp.network.request import Request
from palp.filter.filter_base import BaseFilter, FilterLock


class RequestMemoryFilter(BaseFilter):
    def __init__(self):
        self.memory_filter_request = set()
        self.memory_filter_item = set()

    def is_repeat(self, obj, **kwargs) -> bool:
        """
        获取对应的指纹，通过 python 的 set 去重

        :param obj:
        :param kwargs:
        :return:
        """
        fingerprint_md5 = self.fingerprint(obj=obj)

        if isinstance(obj, Request):
            memory_filter = self.memory_filter_request
        else:
            memory_filter = self.memory_filter_item

        with FilterLock():
            if fingerprint_md5 in memory_filter:
                return True

            memory_filter.add(fingerprint_md5)

            return False

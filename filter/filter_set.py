"""
    本地内存去重

    print(MemoryFilter.is_repeat(request=RequestGet(url='https://www.baidu.com')))
    print(MemoryFilter.is_repeat(request=RequestGet(url='https://www.baidu.com')))
"""
from palp import settings
from palp.network.request import Request
from palp.filter.filter import FilterBase, FilterLock


class SetFilter(FilterBase):
    def __init__(self):
        self.memory_filter_request = set()
        self.memory_filter_item = set()

    def is_repeat(self, obj, **kwargs):
        """
        获取对应的指纹，通过 python 的 set 去重

        :param obj:
        :param kwargs:
        :return:
        """
        fingerprint = self.fingerprint(obj=obj)

        if isinstance(obj, Request):
            memory_filter = self.memory_filter_request
        else:
            memory_filter = self.memory_filter_item

        if settings.STRICT_FILTER:
            with FilterLock():
                return self.judge(memory_filter, fingerprint)
        else:
            return self.judge(memory_filter, fingerprint)

    def judge(self, f, fingerprint):
        """
        进行判断

        :param f: 判断条件或方法之类
        :param fingerprint: 指纹
        :return:
        """
        if fingerprint in f:
            return True

        f.add(fingerprint)

        return False

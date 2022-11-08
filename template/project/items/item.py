"""
    通过 item 将数据传输至 pipeline
"""
import palp


class Item(palp.Item):
    def __init__(self, **kwargs):
        # 懒人方式
        for key, value in kwargs.items():
            setattr(self, key, value)

        # 一般方式
        # self.xxx = kwargs.get('xxx')

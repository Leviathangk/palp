"""
    通用、懒人 item

    示例：
        yield LazyItem(**{'x':'y'})
"""
from palp.item.item import Item


class LazyItem(Item):
    """
        通用、懒人 item
    """

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            self[key] = value

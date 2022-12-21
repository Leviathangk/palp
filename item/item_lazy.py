"""
    通用、懒人 item

    示例：
        yield LazyItem(**{'x':'y'})
"""
import palp


class LazyItem(palp.Item):
    """
        通用、懒人 item
    """

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            self[key] = value

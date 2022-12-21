"""
    通过 item 将数据传输至 pipeline
"""
import palp


class LazyItem(palp.LazyItem):
    """
        通用、懒人 item
    """


class StrictItem(palp.StrictItem):
    """
        严格 item
    """
    # 此处需要定义数据库字段
    # name = palp.Field()

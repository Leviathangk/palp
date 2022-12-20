"""
    严格的 item（类似 scrapy item）

    示例
        class ItemStrict(palp.ItemStrict):
            name = palp.Field()
"""
from palp.item.item import ItemBase, Field
from palp.exception import NotStrictItemFieldException


class StrictItemBase(ItemBase):
    """
        严格的 item，对 init 字段进行判断是否在运行的列表内
    """

    def __new__(cls, *args, **kwargs):
        """
        不使用 scrapy 的元类方式，但思想一致
        给每一个创建的类添加 palp_fields 字段来对输入字段去重

        :param args:
        :param kwargs:
        """
        cls.palp_fields = []

        for field, field_class in cls.__dict__.items():
            if isinstance(field_class, Field):
                cls.palp_fields.append(field)

        return object.__new__(cls)

    def __init__(self, **kwargs):
        for field, field_value in kwargs.items():
            if field not in self.__class__.palp_fields:
                raise NotStrictItemFieldException(f"字段 {field} 不在 {self.__class__.__name__} 允许字段列表中")

            self[field] = field_value


class StrictItem(StrictItemBase):
    """
        对 init 字段进行判断的 item
    """

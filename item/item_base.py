"""
    基础的 item

    要实现 Item() == {} 必须继承 MutableMapping
    必须实现 item 的方法、__len__、__iter__ 方法

    案例：
        class Item(palp.Item):
            def __init__(self, **kwargs):
                # 懒人方式
                for key, value in kwargs.items():
                    self[key] = value

                # 一般方式
                # self.xxx = kwargs.get('xxx')
"""
import json
from loguru import logger
from typing import MutableMapping


class BaseItem(MutableMapping):
    def to_dict(self) -> dict:
        """
        转化为 dict

        :return:
        """
        item = {}

        for key, value in self.__dict__.items():
            item[key] = value

        return item

    def to_json(self, **kwargs) -> str:
        """
        转化为 json

        :param kwargs: json 参数
        :return:
        """
        kwargs.setdefault('ensure_ascii', False)

        return json.dumps(self.to_dict(), **kwargs)

    def keys(self):
        """
        使类可以遍历 keys

        :return:
        """
        for key in self.__dict__.keys():
            yield key

    def values(self):
        """
        使类可以遍历 values

        :return:
        """
        for value in self.__dict__.values():
            yield value

    def items(self):
        """
        使类可以遍历 items

        :return:
        """
        for key, value in self.__dict__.items():
            yield key, value

    def __setattr__(self, key, value):
        """
        这是属性，但是做的是字典，虽然可以但是不建议

        :param key:
        :param value:
        :return:
        """
        logger.warning(f"请使用 item['xxx'] = xxx 而不是 item.xxx = xxx！")

        self.__dict__[key] = value

    def __getattr__(self, item):
        """
        这是属性，但是做的是字典，虽然可以但是不建议

        :param item:
        :return:
        """
        logger.warning(f"请使用 item['xxx'] 而不是 item.xxx！")

        return self.__dict__.get(item)

    def __setitem__(self, key, value):
        """
        使类可以通过 xxx['xxx'] = xxx 进行设置

        :param key:
        :param value:
        :return:
        """
        self.__dict__[key] = value

    def __getitem__(self, item):
        """
        使类可以通过 xxx['xxx'] 进行访问

        :param item:
        :return:
        """
        return self.__dict__.get(item)

    def __delitem__(self, key):
        """
        使类可以通过 del xxx['xxx'] 进行移除

        :param key:
        :return:
        """
        if key in self.__dict__:
            del self.__dict__[key]

    def __len__(self):
        """
        使类可使用 len()

        :return:
        """
        return len(self.__dict__)

    def __iter__(self):
        """
        使类可遍历

        :return:
        """
        return iter(self.__dict__)

    def __str__(self):
        return f"<{self.__class__.__name__} item:{self.to_dict()}>"


class Item(BaseItem):
    """
    外部引用使用
    """

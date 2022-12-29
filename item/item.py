"""
    基础的 item

    要实现 Item() == {} 必须继承 MutableMapping 必须实现 item 的方法、__len__、__iter__ 方法

    注意：
        通过 isinstance 还是不能判断出是 dict，所以部分场景需要 to_dict
"""
import json
from typing import MutableMapping


class Field:
    """
        定义字段
    """


class ItemBase(MutableMapping):
    def to_dict(self) -> dict:
        """
        转化为 dict

        :return:
        """
        return self.__dict__

    def to_json(self, **kwargs) -> str:
        """
        转化为 json

        :param kwargs: json 参数
        :return:
        """
        kwargs.setdefault('ensure_ascii', False)

        return json.dumps(self.to_dict(), **kwargs)

    def __setattr__(self, key, value):
        """
        设置属性（不提倡，但允许）

        :param key:
        :param value:
        :return:
        """
        self.__dict__[key] = value

    def __getattr__(self, item):
        """
        获取属性（不提倡，但允许）

        :param item:
        :return:
        """
        return self.__dict__[item]

    def __delattr__(self, item):
        """
        删除属性（不提倡，但允许）

        :param item:
        :return:
        """
        del self.__dict__[item]

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
        return self.__dict__[item]

    def __delitem__(self, key):
        """
        使类可以通过 del xxx['xxx'] 进行移除

        :param key:
        :return:
        """
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

    def __getstate__(self):
        """
        pickle dumps 时使用

        :return:
        """
        return self.to_dict()

    def __setstate__(self, state):
        """
        pickle loads 时使用

        :param state:
        :return:
        """
        self.__dict__.update(state)

    def __str__(self):
        return f"<{self.__class__.__name__} item:{self.to_dict()}>"


class Item(ItemBase):
    """
        item
    """

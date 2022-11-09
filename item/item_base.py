"""
    基础的 item
"""
import json


class BaseItem:
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
        设置属性，也可以通过字典方法访问到

        :param key:
        :param value:
        :return:
        """
        self.__dict__[key] = value

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

    def __str__(self):
        return f"<{self.__class__.__name__} item:{self.to_dict()}>"


class Item(BaseItem):
    """
    外部引用使用
    """

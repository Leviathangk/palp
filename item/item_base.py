"""
    基础的 item

    要实现 Item() == {} 必须继承 MutableMapping
    必须实现 item 的方法、__len__、__iter__ 方法

    注意：
        通过 isinstance 还是不能判断出是 dict，所以部分场景需要 to_dict

    案例：
        class Item(palp.Item):
            def __init__(self, **kwargs):
                # 懒人方式
                for key, value in kwargs.items():
                    self[key] = value
                    或者
                    setattr(self, key, value)

                # 一般方式
                # self.xxx = kwargs.get('xxx')
"""
import json
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

    def __setattr__(self, key, value):
        """
        设置属性

        :param key:
        :param value:
        :return:
        """
        self.__dict__[key] = value

    def __getattr__(self, item):
        """
        获取属性

        :param item:
        :return:
        """
        return self.__dict__[item]

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

    def __str__(self):
        return f"<{self.__class__.__name__} item:{self.to_dict()}>"


class Item(BaseItem):
    """
    外部引用使用
    """

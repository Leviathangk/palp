"""
    meta 会在 request 中自动传递，避免每次都传
"""
import json
from typing import MutableMapping


class Meta(MutableMapping):
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

    def __setitem__(self, key, value):
        """
        设置值

        :param key: 键
        :param value: 值
        :return:
        """
        self.__dict__[key] = value

    def __getitem__(self, key):
        """
        获取 value

        :param key: 键
        :return:
        """
        if key in self.__dict__:
            return self.__dict__[key]

    def __delitem__(self, key):
        """
        删除 key

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
        return self.to_json()

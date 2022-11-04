"""
    基础的 item
"""
import json


class BaseItem:
    table = None  # 表名

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

    def __str__(self):
        return f"<{self.__class__.__name__} table:{self.__class__.table} item:{self.to_dict()}>"

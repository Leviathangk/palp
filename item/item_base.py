"""
    基础的 item
"""
import json
from loguru import logger


class BaseItem:
    __table_name__ = None  # 表名

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
        if not isinstance(key, str):
            logger.warning("item key 必须是一个字符串")
            key = str(key)

        self.__dict__[key] = value

    def __str__(self):
        return f"<{self.__class__.__name__} table:{self.__class__.__table_name__} item:{self.to_dict()}>"

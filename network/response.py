"""
    返回带有解析器功能的 Response
"""

import re
import time
import requests
from typing import Any
from palp import settings
from parsel import Selector
from requests.models import Response as RequestResponse


# 响应解析器
class Response(RequestResponse):
    def __init__(self, resp: RequestResponse):
        """

        :param resp: requests 返回的响应
        """
        super().__init__()
        self._resp = resp
        self._resp.encoding = resp.apparent_encoding
        self._selector = Selector(self._resp.text)

        self.__dict__.update(self._resp.__dict__)  # 把 request Response 对象的数据转移过来

    def json(self, **kwargs) -> Any:
        return self._resp.json(**kwargs)

    def xpath(self, query: str, namespaces: str = None, **kwargs):
        """
        实现 xpath 选择器功能

        :param query: 匹配规则
        :param namespaces: 命名空间
        :param kwargs:
        :return:
        """
        return self._selector.xpath(query=query, namespaces=namespaces, **kwargs)

    def css(self, query: str):
        """
        实现 css 选择器功能

        :param query: 匹配规则
        :return:
        """
        return self._selector.css(query=query)

    def re(self, pattern: str, flags=0) -> list:
        """
        常用 flags：
            re.I：忽略字母大小写
            re.A：匹配相应的 ASCII 字符类别

        :param pattern: 匹配规则
        :param flags: 修饰符
        :return:
        """
        return re.findall(pattern, self.text, flags=flags)

    def re_first(self, pattern: str, flags=0) -> str:
        """
        常用 flags：
            re.I：忽略字母大小写
            re.A：匹配相应的 ASCII 字符类别

        :param pattern: 匹配规则
        :param flags: 修饰符
        :return:
        """
        result = self.re(pattern=pattern, flags=flags)
        if result:
            return result[0]

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __getattr__(self, item):
        return self.__dict__.get(item)


# 发起请求，返回响应，含有 session 功能
class ResponseDownloader:

    def __init__(self, keep_session: bool, session: requests.Session):
        """

        :param keep_session: 是否需要保持 session
        :param session: session
        """
        self.keep_session = keep_session
        self.session = session

    def response(self, **kwargs) -> Response:
        time.sleep(settings.REQUEST_DELAY)  # 请求等待延迟

        if self.keep_session:
            resp = self.session.request(**kwargs)
        else:
            resp = requests.request(**kwargs)

            # 更新请求的 cookie、响应的 cookie
            self.session.cookies.update(kwargs['cookies'])
            self.session.cookies.update(resp.cookies.get_dict())

        return Response(resp)

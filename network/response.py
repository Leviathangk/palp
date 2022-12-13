"""
    返回带有解析器功能的 Response

    注意：
        这里没有强制实现所有方法，但是一定要有 text、url、cookies
"""

import re
import chardet
from parsel import Selector
from abc import abstractmethod
from urllib.parse import urljoin


class Response:
    """
        根据响应体，解析响应
    """

    def __init__(self, resp):
        """

        :param resp: requests 返回的响应
        """
        self.response = resp
        self._selector = None

    @property
    @abstractmethod
    def text(self) -> str:
        """
        文本方法

        :return:
        """

    @property
    def content(self) -> bytes:
        """
        二进制 content

        :param args:
        :param kwargs:
        :return:
        """

    def json(self, *args, **kwargs) -> dict:
        """
        json 方法

        :return:
        """

    @property
    def status_code(self) -> int:
        """
        状态码

        :return:
        """

    @property
    @abstractmethod
    def cookies(self) -> dict:
        """
        返回 cookies，实在没有返回空字典： {}

        :return:
        """

    @property
    def headers(self) -> dict:
        """
        返回 请求头

        :return:
        """

    @property
    @abstractmethod
    def url(self) -> str:
        """
        响应 url

        :return:
        """

    @property
    def history(self) -> list:
        """
        响应 历史

        :return:
        """

    @property
    def links(self) -> dict:
        """

        :return:
        """

    @property
    def encoding(self):
        return chardet.detect(self.content)["encoding"]

    @property
    def selector(self):
        if self._selector is None:
            self._selector = Selector(self.text)

        return self._selector

    def xpath(self, query: str, namespaces: str = None, **kwargs):
        """
        实现 xpath 选择器功能

        :param query: 匹配规则
        :param namespaces: 命名空间
        :param kwargs:
        :return:
        """
        return self.selector.xpath(query=query, namespaces=namespaces, **kwargs)

    def css(self, query: str):
        """
        实现 css 选择器功能

        :param query: 匹配规则
        :return:
        """
        return self.selector.css(query=query)

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

    def urljoin(self, url: str):
        """
        合并 url

        :return:
        """
        return urljoin(self._resp.url, url)

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __getattr__(self, item):
        return self.__dict__.get(item)

    def __str__(self):
        return f'<Response [{self.response.status_code}]>'

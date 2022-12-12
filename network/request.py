"""
    请求的处理
"""
import time
import random
import urllib3
from palp import settings
from typing import Callable
from urllib.parse import urlparse
from palp.network.response import Response
from palp.tool.user_agent import random_ua
from requests.cookies import RequestsCookieJar
from palp.tool.short_module import import_module
from urllib3.exceptions import InsecureRequestWarning

# 禁用不安全警告
urllib3.disable_warnings(InsecureRequestWarning)


class Request:
    # requests 模块所需的
    __REQUEST_ATTRS__ = [
        'url',
        'method',
        'params',
        'data',
        'headers',
        'cookies',
        'files',
        'auth',
        'timeout',
        'allow_redirects',
        'proxies',
        'hooks',
        'stream',
        'verify',
        'cert',
        'json',
    ]

    # 框架运行所需的
    __PALP_ATTRS__ = [
        'filter_repeat',
        'keep_session',
        'keep_cookie',
        'new_session',
        'callback',
        'cookie_jar',
        'priority',
        'command'
    ]

    # 下载器
    DOWNLOADER = None
    DOWNLOADER_PARSER = None

    def __new__(cls, *args, **kwargs):
        """
        导入下载器

        :param args:
        :param kwargs:
        """
        if cls.DOWNLOADER is None:
            cls.DOWNLOADER = import_module(settings.RESPONSE_DOWNLOADER, instantiate=False)[0]
            cls.DOWNLOADER_PARSER = import_module(settings.RESPONSE_DOWNLOADER_PARSER, instantiate=False)[0]

        return object.__new__(cls)

    def __init__(
            self,
            url: str,
            method: str = None,
            params=None,
            data=None,
            headers=None,
            cookies=None,
            timeout=None,
            proxies=None,
            json=None,
            downloader=None,
            filter_repeat: bool = False,
            keep_session: bool = False,
            keep_cookie: bool = False,
            callback: Callable = None,
            cookie_jar: RequestsCookieJar = None,
            priority: int = settings.DEFAULT_QUEUE_PRIORITY,
            command: dict = None,
            **kwargs
    ):
        """
        requests 参数
        :param url: 请求链接
        :param params: params
        :param data: data
        :param headers: 请求头
        :param cookies: cookies
        :param timeout: 超时时间
        :param proxies: 代理：{'http':'http://ip:port','https':'https://ip:port'}
        :param json: json：也可以使用 data = json.dumps(data)

        Palp 参数
        :param filter_repeat: 是否过滤请求，settings.FILTER_REQUEST 启用生效，默认 False
        :param keep_session: 是否保持 session，默认 False
        :param keep_cookie: 不使用 session 时保持 cookie，默认 False
        :param callback: 回调函数
        :param priority: 启用优先级队列时的优先级，分数越大，优先级约低，默认 settings.DEFAULT_QUEUE_PRIORITY
        :param command: 自定义操作命令，用于自定义 downloader 时使用

        Palp 参数（非用户设置）
        :param cookie_jar: cookie_jar，存储 cookie，这里使用的是 requests 模块的，其它请求的话可以自己提取

        传递的参数
        :param kwargs: 其余需要传递的参数，若参数名不存在则返回 None
        """

        # Request 所需字段
        self._requests_params = {}  # request 参数
        self.command = command
        self.callback = callback
        self.priority = priority
        self.downloader = downloader
        self.cookie_jar = cookie_jar
        self.keep_cookie = keep_cookie
        self.keep_session = keep_session
        self.filter_repeat = filter_repeat

        # requests 请求参数
        self.url = url
        self.data = data
        self.json = json
        self.method = method
        self.params = params
        self.headers = headers
        self.cookies = cookies
        self.timeout = timeout
        self.proxies = proxies

        # 传递参数更新一下
        for key, value in kwargs.items():
            self[key] = value

    def send(self) -> Response:
        """
        获取响应

        :return: ResponseParser 的解析器
        """
        # 加载默认值
        self.set_default()

        # 判断是否等待
        if isinstance(settings.REQUEST_DELAY, int) or isinstance(settings.REQUEST_DELAY, float):
            time.sleep(settings.REQUEST_DELAY)
        elif isinstance(settings.REQUEST_DELAY, list):
            time.sleep(random.choice([i for i in range(settings.REQUEST_DELAY[0], settings.REQUEST_DELAY[1] + 1)]))

        # 获取响应
        response = self.downloader(
            **self._requests_params,
            keep_session=self.keep_session,
            keep_cookie=self.keep_cookie,
            cookie_jar=self.cookie_jar,
            command=self.command
        ).response()

        response_parser = self.__class__.DOWNLOADER_PARSER(response)  # 解析器解析响应
        if response_parser.cookies:
            self.cookie_jar.update(response_parser.cookies)  # 将响应的 cookie 更新到 cookieJar

        return response_parser

    def set_default(self):
        """
        设置一些默认值

        :return:
        """
        # 判断类型
        if self.method:
            self.method = self.method.upper()
        elif self.data or self.json:
            self.method = 'POST'
        else:
            self.method = 'GET'

        # 设置默认
        if self.downloader is None:
            self.downloader = self.__class__.DOWNLOADER
        if self.cookie_jar is None:
            self.cookie_jar = RequestsCookieJar()
        if self.command is None:
            self.command = {}
        if self.headers is None:
            self.headers = {}
        if self.cookies is None:
            self.cookies = {}
        if self.timeout is None:
            self.timeout = settings.REQUEST_TIMEOUT or 60
        self._requests_params.setdefault('verify', False)

        # 添加 ua（模块在使用 ua 的时候可能访问降速）
        if settings.RANDOM_USERAGENT:
            ua = random_ua()
        else:
            ua = settings.DEFAULT_USER_AGENT

        if not self.headers:
            self.headers.update({'User-Agent': ua})
        elif self.headers.get('User-Agent'):
            self.headers.update({'User-Agent': ua})
        elif self.headers.get('user-agent'):
            self.headers.update({'user-agent': ua})

    def to_dict(self) -> dict:
        """
        获取字典形式

        主要作用：快速进行二次请求

        示例：
            request_dict = request.to_dict()
            request_dict[xxx] = xxx # 修改

            yield palp.Request(**request_dict)
        :return:
        """
        request_dict = {}

        for key, value in self.__dict__.items():
            if key.startswith('_') or not value:
                continue
            request_dict[key] = value

        return request_dict

    @property
    def domain(self) -> str:
        """
        获取请求的域名

        :return:
        """
        return urlparse(self.url).netloc

    def __getattr__(self, item):
        """
        可以 request.xxx 进行访问，但是这里严格一点没有就报错避免误导

        :param item:
        :return:
        """
        if item in self.__dict__:
            return self.__dict__[item]

        raise AttributeError(f'未定义的属性：{item}')

    def __setattr__(self, key, value):
        """
        实现 requests.xxx 设置参数（只有 self.xxx 才会进入该函数）

        @param key:
        @param value:
        @return:
        """
        self.__dict__[key] = value

        if key in self.__class__.__REQUEST_ATTRS__:
            self._requests_params[key] = value

    def __lt__(self, other):
        """
        返回比较，否则使用优先级队列会报错

        :param other:
        :return:
        """
        return self.priority < other.priority

    def __str__(self):
        return f"<Request {self.method}-{self.url}>"

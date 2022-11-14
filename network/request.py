"""
    请求的处理
"""
import urllib3
import requests
from palp import settings
from typing import Callable
from urllib.parse import urlparse
from palp.tool.user_agent import random_ua
from requests.cookies import RequestsCookieJar
from palp.network.response import ResponseDownloader
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
        'callback',
        'session',
        'cookie_jar'
    ]

    def __init__(self, url: str = None, method: str = None, params=None, data=None, headers=None, cookies=None,
                 files=None, auth=None, timeout=None, allow_redirects=True, proxies=None, hooks=None, stream=None,
                 verify=None, cert=None, json=None, filter_repeat: bool = None, keep_session: bool = None,
                 callback: Callable = None, level: int = None, session: requests.Session = None,
                 cookie_jar: RequestsCookieJar = None, **kwargs):
        """
        requests 参数
        :param url: 请求链接
        :param params: params
        :param data: data
        :param headers: 请求头
        :param cookies: cookies
        :param files: 文件：{ file_name:open(file) }
        :param auth: 身份验证
        :param timeout: 超时时间
        :param allow_redirects: 允许重定向：默认 True
        :param proxies: 代理：{'http':'http://ip:port','https':'https://ip:port'}
        :param hooks: 钩子：{'response':func}
        :param stream: 流传输
        :param verify: 证书验证：默认 False
        :param cert: ssl 证书路径
        :param json: json：也可以使用 data = json.dumps(data)

        Palp 参数
        :param filter_repeat: 是否过滤请求
        :param keep_session: 是否保持 session
        :param callback: 回调函数
        :param level: 启用优先级队列时的优先级，分数越大，优先级约低

        Palp 参数（非用户设置）
        :param session: session 保证每个线程都是独立的
        :param cookie_jar: cookie_jar，存储 cookie

        传递的参数
        :param kwargs: 其余需要传递的参数，若参数名不存在则返回 None
        """

        # Request 所需字段
        self._requests_params = {}  # request 参数
        self.keep_session = keep_session or False
        self.filter_repeat = filter_repeat or False
        self.callback = callback
        self.session = session or requests.session()
        self.level = level or 100
        self.cookie_jar = cookie_jar or RequestsCookieJar()

        # requests 请求参数
        self.url = url
        self.method = method
        self.params = params
        self.data = data
        self.headers = headers or {}
        self.cookies = cookies
        self.files = files
        self.auth = auth
        self.timeout = timeout or settings.REQUEST_TIMEOUT or 60
        self.allow_redirects = allow_redirects
        if not proxies and settings.REQUEST_PROXIES_TUNNEL_URL:
            proxies = {'http': settings.REQUEST_PROXIES_TUNNEL_URL, 'https': settings.REQUEST_PROXIES_TUNNEL_URL}
        self.proxies = proxies
        self.hooks = hooks
        self.stream = stream
        self.verify = verify
        self.cert = cert
        self.json = json

        # 传递参数更新一下
        for key, value in kwargs.items():
            self.__dict__[key] = value

        # 判断类型
        if self.method:
            self.method = self.method.upper()
        elif self.data or self.json:
            self.method = 'POST'
        else:
            self.method = 'GET'

        # 添加 ua
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

    def send(self):
        """

        :return: ResponseParser 的解析器
        """
        response = ResponseDownloader(
            keep_session=self.keep_session,
            session=self.session,
            cookie_jar=self.cookie_jar
        ).response(**self._requests_params)

        return self.callback, response

    def add_proxy(self, proxies: str = None, allow_domains: list = None) -> None:
        """
        指定域名添加代理

        代理选用优先级：proxies > self.proxies > settings.REQUEST_PROXIES_TUNNEL_URL

        使用方式：
            1、在 RequestMiddleware 中的 request_in 中建立 allow_domains 列表
            2、使用 request.add_proxy(allow_domains=allow_domains)

        :param proxies: 代理
        :param allow_domains: 允许的域名（middleware 中使用）
        :return:
        """
        if isinstance(self.proxies, tuple):
            self.proxies = dict(self.proxies)
        if isinstance(self.proxies, dict):
            proxies_input = list(self.proxies.values())[0]
        else:
            proxies_input = self.proxies

        proxies = proxies or proxies_input or settings.REQUEST_PROXIES_TUNNEL_URL
        if not proxies:
            return

        if allow_domains:
            if self.domain in allow_domains:
                self.proxies = {'http': proxies, 'https': proxies}
            else:
                self.proxies = None
        else:
            self.proxies = {'http': proxies, 'https': proxies}

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
            if key.startswith('_'):
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
        return self.level < other.level

    def __str__(self):
        return f"<Request {self.method}-{self.url}>"

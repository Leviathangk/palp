"""
    请求的处理
"""
import urllib3
import requests
from palp import settings
from typing import Callable
from palp.tool.user_agent import random_ua
from requests.cookies import RequestsCookieJar
from palp.network.response import ResponseDownloader
from urllib3.exceptions import InsecureRequestWarning

# 禁用不安全警告
urllib3.disable_warnings(InsecureRequestWarning)


class Request:
    # requests 模块所需的
    REQUEST_ATTRS = [
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
    PALP_ATTRS = [
        'filter_repeat',
        'keep_session',
        'callback',
        'render',
        'render_time',
        'session',
        'cookie_jar'
    ]

    def __init__(self, url: str = None, method: str = None, params=None, data=None, headers=None, cookies=None,
                 files=None, auth=None, timeout=None, allow_redirects=True, proxies=None, hooks=None, stream=None,
                 verify=None, cert=None, json=None, filter_repeat: bool = None, keep_session: bool = None,
                 callback: Callable = None, render: bool = None, render_time: int = None, level: int = None,
                 session: requests.Session = None, cookie_jar: RequestsCookieJar = None, **kwargs):
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
        :param render: 是否用浏览器渲染
        :param render_time: 等待页面加载最大时间
        :param level: 启用优先级队列时的优先级，分数越大，优先级约低

        Palp 参数（非用户设置）
        :param session: session 保证每个线程都是独立的
        :param cookie_jar: cookie_jar，存储 cookie

        传递的参数
        :param kwargs: 其余需要传递的参数，若参数名不存在则返回 None
        """

        # Request 所需字段
        self._requests_params = {}  # request 参数
        self._original_params = {}  # __init__ 后的 request 参数，用来传递快速发起请求
        self.keep_session = keep_session or False
        self.filter_repeat = filter_repeat or False
        self.callback = callback
        self.render = render or False
        self.render_time = render_time or 60
        self.session = session or requests.session()
        self.level = level or 10
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

        self._original_params.update(kwargs)

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

        # 给响应体携带上请求原数据（非纯原）
        response.__dict__.update({
            'palp': {
                'requests': self._original_params
            }
        })

        return self.callback, response

    def __setattr__(self, key, value):
        """
        实现 requests.xxx 设置参数（只有 self.xxx 才会进入该函数）

        @param key:
        @param value:
        @return:
        """
        self.__dict__[key] = value

        if key in self.__class__.REQUEST_ATTRS:
            self._requests_params[key] = value

        if not key.startswith('_'):
            self._original_params[key] = value

    def __str__(self):
        return f"<Request {self.method}-{self.url}>"

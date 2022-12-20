"""
    请求器

    注意：
        自定义 downloader 如果使用 keep_session
        需要自定义 __new__ 参考 palp.network.downloader_requests.ResponseDownloaderByRequests
"""
import threading
from abc import abstractmethod
from urllib.parse import urlparse
from requests.cookies import RequestsCookieJar


class ResponseDownloader:
    """
        网络请求响应器
    """
    SESSION = None  # session 该参数一定要覆写，不然单进程内多线程使用多种 downloader 会被覆盖

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
            cookie_jar: RequestsCookieJar = None,
            keep_session: bool = False,
            keep_cookie: bool = False,
            command: dict = None,
            **kwargs
    ):
        """

        :param keep_session: 是否保持 session
        :param keep_cookie: 是否保持 cookie，启用 session 则不用 cookie_jar
        :param command: 自定义命令
        :param kwargs: 不在常用命令里的请求命令
        """
        # 请求参数
        self.url = url
        self.method = method
        self.params = params
        self.data = data
        self.headers = headers
        self.cookies = cookies
        self.timeout = timeout
        self.proxies = proxies
        self.json = json
        self.kwargs = kwargs

        # 其余参数
        self.keep_session = keep_session
        self.keep_cookie = keep_cookie
        self.cookie_jar = cookie_jar
        self.command = command

    @abstractmethod
    def response(self):
        """
        处理响应并返回

        :return:
        """

    @property
    def domain(self) -> str:
        """
        获取请求的域名

        :return:
        """
        return urlparse(self.url).netloc

    @property
    def ident(self) -> int:
        """
        返回当前线程的线程号，保证线程间独立

        :return:
        """
        return threading.current_thread().ident

    @property
    def session(self):
        """
        获取 session 的快捷方式

        :return:
        """
        return self.__class__.SESSION

"""
    requests 请求器
"""
import requests
from requests.adapters import HTTPAdapter
from palp.network.downloader import ResponseDownloader


class ResponseDownloaderByRequests(ResponseDownloader):
    """
        适用于 requests 的请求器
    """
    SESSION = None

    def __new__(cls, *args, **kwargs):
        """
        requests 设置 session

        :param args:
        :param kwargs:
        """
        if cls.SESSION is None:
            cls.SESSION = requests.Session()
            cls.SESSION.mount("http", HTTPAdapter(pool_connections=1000, pool_maxsize=1000))

        return object.__new__(cls)

    def response(self):
        """
        处理响应并返回

        :return:
        """
        # 获取请求器
        if self.keep_session:
            request = self.session
        else:
            request = requests

        # 是否保持 cookie
        if not self.keep_session and self.keep_cookie:
            self.cookies = self.cookie_jar

        return request.request(
            url=self.url,
            method=self.method,
            params=self.params,
            data=self.data,
            headers=self.headers,
            cookies=self.cookies,
            timeout=self.timeout,
            proxies=self.proxies,
            json=self.json,
            **self.kwargs
        )

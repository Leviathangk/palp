"""
    httpx 请求器
"""
import httpx
from loguru import logger
from palp import settings
from palp.network.downloader import ResponseDownloader


class ResponseDownloaderByHttpx(ResponseDownloader):
    """
        适用于 httpx 的请求器
    """
    SESSION = None

    def __new__(cls, *args, **kwargs):
        """
        httpx 设置 session

        注意：
            httpx 的 session 比较麻烦。设置代理必须设置时就加上，建议自定义
            http2 的话也得在这里设置，建议自定义

        :param args:
        :param kwargs:
        """
        if cls.SESSION is None:
            if settings.REQUEST_PROXIES_TUNNEL_URL:
                proxies = {"all://": settings.REQUEST_PROXIES_TUNNEL_URL}
            else:
                proxies = None
            cls.SESSION = httpx.Client(proxies=proxies)

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
            request = httpx

        # 是否保持 cookie
        if not self.keep_session and self.keep_cookie:
            if self.cookies:
                self.cookie_jar.update(self.cookies)
            self.cookies = self.cookie_jar

        # 构建请求参数
        httpx_kwargs = dict(
            url=self.url,
            method=self.method,
            params=self.params,
            data=self.data,
            headers=self.headers,
            cookies=self.cookies,
            timeout=self.timeout,
            json=self.json,
        )

        httpx_kwargs.update(self.kwargs)

        # 请求参数判断
        if self.keep_session and self.proxies:
            logger.warning(
                'httpx 不支持在使用 session 时，使用 proxies 参数，仅支持预设，请自定义：palp.network.downloader_requests.ResponseDownloaderByHttpx'
            )

            del httpx_kwargs['proxies']

        return request.request(**httpx_kwargs)

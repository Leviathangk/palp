"""
    请求检查中间件
"""
from loguru import logger
from palp import settings
from urllib.parse import urlparse
from palp.exception.exception_drop import DropRequestException
from palp.middleware.middleware_request_base import RequestMiddleware


class RequestCheckMiddleware(RequestMiddleware):
    def request_in(self, spider, request) -> None:
        # 判断使用过滤时是否开启了过滤
        if request.filter_repeat and not settings.REQUEST_FILTER:
            logger.warning(f'过滤请求请将 settings.REQUEST_FILTER 设置为 True，当前请求：{request.url}')

        # 判断域名是否在可用域名内
        domains = spider.__class__.spider_domains
        if isinstance(domains, list) and len(domains) != 0:
            domain = urlparse(request.url).netloc
            if domain not in domains:
                raise DropRequestException()

"""
    请求检查中间件
"""
from loguru import logger
from palp import settings
from urllib.parse import urlparse
from palp.exception import DropRequestException
from palp.middleware.middleware_request import RequestMiddleware


class RequestCheckMiddleware(RequestMiddleware):
    """
        请求检查中间件
    """

    def request_in(self, spider, request):
        # 过滤开启检查，请求开启过滤，设置没开启过滤抛出警告
        if request.filter_repeat and not settings.FILTER_REQUEST:
            logger.warning(f'过滤请求请将 settings.REQUEST_FILTER 设置为 True，当前请求：{request.url}')

        # 域名检查，非指定域名则抛出
        domains = spider.__class__.spider_domains
        if isinstance(domains, list) and len(domains) != 0:
            domain = urlparse(request.url).netloc
            if domain not in domains:
                raise DropRequestException()

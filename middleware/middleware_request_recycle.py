"""
    request 失败回收中间件
"""
from palp import settings
from palp.middleware.middleware_request import RequestMiddleware


class RequestRecycleMiddleware(RequestMiddleware):
    """
        失败请求回收中间件
    """

    def request_failed(self, spider, request):
        """
        回收失败的请求

        注意：开启 REQUEST_FAILED_SAVE 才会启用

        :param spider:
        :param request:
        :return:
        """
        from palp.conn import redis_conn

        if redis_conn is None and settings.SPIDER_TYPE == 1:
            return

        redis_conn.sadd(settings.REDIS_KEY_QUEUE_BAD_REQUEST, request.to_json())

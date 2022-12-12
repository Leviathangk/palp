"""
    request 失败回收中间件
"""
import json
from palp import settings
from palp.middleware.middleware_request import RequestMiddleware


class RequestRecycleMiddleware(RequestMiddleware):
    """
        失败请求回收中间件
    """

    def request_failed(self, spider, request):
        """
        回收失败的请求，为了能够直观的展示，就不使用 pickle 了

        注意：开启 REQUEST_FAILED_SAVE 才会启用

        :param spider:
        :param request:
        :return:
        """
        from palp.conn import redis_conn

        if redis_conn is None:
            return

        req = request.to_dict()
        if req['callback']:
            req['callback'] = req['callback'].__name__
        req['cookies'] = req['cookie_jar'].get_dict()

        del req['cookie_jar']

        redis_conn.sadd(settings.REDIS_KEY_QUEUE_BAD_REQUEST, json.dumps(req, ensure_ascii=False))

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

        # 保存请求
        req = request.to_dict()

        # 转化 callback
        if request.callback:
            req['callback'] = req['callback'].__name__

        # 转化 cookie_jar
        if request.cookie_jar:
            if request.cookies:
                request.cookie_jar.update(request.cookies)
            req['cookies'] = request.cookie_jar.get_dict()
            del req['cookie_jar']

        # 转化 downloader
        if request.downloader != request.__class__.DOWNLOADER:
            req['downloader'] = {
                'module': request.downloader.__module__,  # 引用自哪里（downloader 都是未实例化的所以不需要 __class__）
                'init': request.downloader.__name__,  # 模块名叫什么
            }
        else:
            del req['downloader']

        # 转化 downloader_parser
        if request.downloader_parser != request.__class__.DOWNLOADER_PARSER:
            req['downloader_parser'] = {
                'module': request.downloader_parser.__module__,  # 引用自哪里
                'init': request.downloader_parser.__name__,  # 模块名叫什么
            }
        else:
            del req['downloader_parser']

        # 删除代理
        if request.proxies:
            del req['proxies']

        redis_conn.sadd(settings.REDIS_KEY_QUEUE_BAD_REQUEST, json.dumps(req, ensure_ascii=False))

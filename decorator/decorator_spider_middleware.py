"""
    spider 中间件装饰器
"""
from loguru import logger


class SpiderMiddlewareDecorator:
    """
        spider 中间件装饰器
    """

    def __call__(self, func):
        def _wrapper(*args, **kwargs):
            spider = args[0]  # 其实就是获取 self
            middlewares = spider.__class__.SPIDER_MIDDLEWARE  # 获取 middleware

            for middleware in middlewares:
                middleware.spider_start(spider)

            try:
                func(*args, **kwargs)
            except Exception as e:
                for middleware in middlewares:
                    middleware.spider_error(spider, e)
            finally:
                for middleware in middlewares:
                    try:
                        middleware.spider_close(spider)
                    except Exception as e:
                        logger.exception(e)

        return _wrapper

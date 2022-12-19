"""
    等待 spider 各项功能执行结束
"""


class SpiderWaitDecorator:
    """
        等待 spider controller、item controller 执行完毕
    """

    def __call__(self, func):
        def _wrapper(*args, **kwargs):
            # 先执行函数
            try:
                func(*args, **kwargs)
            finally:
                # 获取 spider
                spider = args[0]

                # 等待 spider 控制器执行结束
                spider.wait_spider_controller_done()

                # 等待 spider item 分发执行完毕
                spider.wait_item_controller_done()

        return _wrapper

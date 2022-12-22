"""
    通过线程执行函数，简化创建线程
"""
import threading
from typing import Callable


class RunByThreadDecorator:
    """
        通过线程执行函数，简化创建线程
    """

    def __init__(self, callback: Callable = None, **kwargs):
        """

        :param callback: 回调函数
        :param kwargs: 线程执行参数
        """
        self.callback = callback
        self.kwargs = kwargs

        self.func_args = None
        self.func_kwargs = None

    def run(self, func: Callable) -> None:
        """

        :param func: 执行函数
        :return:
        """
        res = func(*self.func_args, **self.func_kwargs)
        if self.callback:
            self.callback(res)

    def __call__(self, func: Callable):
        def _wrapper(*args, **kwargs):
            self.func_args = args
            self.func_kwargs = kwargs
            spider = args[0]

            thread = threading.Thread(target=self.run, args=(func,), **self.kwargs)

            if hasattr(spider, 'distribute_thread_list'):
                spider.distribute_thread_list.append(thread)  # 将线程存入列表

            thread.start()

        return _wrapper

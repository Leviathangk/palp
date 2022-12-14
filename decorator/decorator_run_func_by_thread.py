"""
    通过线程执行函数，简化创建线程
"""
import threading
from typing import Callable


class RunByThread(threading.Thread):
    """
        通过线程执行函数，简化创建线程
    """

    def __init__(self, callback: Callable = None, **kwargs):
        super().__init__(**kwargs)
        self.func = None
        self.args = None
        self.kwargs = None
        self.callback = callback

    def run(self) -> None:
        res = self.func(*self.args, *self.kwargs)
        if self.callback:
            self.callback(res)

    def __call__(self, func: Callable):
        def _wrapper(*args, **kwargs):
            spider = args[0]
            if hasattr(spider, 'distribute_thread_list'):
                spider.distribute_thread_list.append(self)  # 将线程存入列表

            self.func = func
            self.args = args
            self.kwargs = kwargs
            self.start()

        return _wrapper

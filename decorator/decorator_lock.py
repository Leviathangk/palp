"""
    线程锁装饰器，直接锁整个函数
"""
import threading
from typing import Callable


class FuncLock:
    """
        通过线程执行函数，简化创建线程
    """

    def __init__(self, timeout: int = -1):
        self.timeout = timeout
        self.lock = threading.RLock()  # 包住整个函数的，所以在实例化里面

    def __call__(self, func: Callable):
        def _wrapper(*args, **kwargs):

            self.lock.acquire(timeout=self.timeout)

            try:
                return func(*args, **kwargs)
            finally:
                self.lock.release()

        return _wrapper

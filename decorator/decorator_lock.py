"""
    线程锁装饰器，直接锁整个函数
"""
import threading
from typing import Callable


class FuncLockDecorator:
    """
        独享锁-线程锁
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


class FuncLockSharedDecorator:
    """
        共享锁-线程锁（用户不要使用该锁）

        一个进程内共享
    """
    LOCK = threading.RLock()  # 包住整个函数的，所以在实例化里面

    def __init__(self, timeout: int = 5):
        self.timeout = timeout

    def __call__(self, func: Callable):
        def _wrapper(*args, **kwargs):

            self.__class__.LOCK.acquire(timeout=self.timeout)

            try:
                return func(*args, **kwargs)
            finally:
                try:
                    self.__class__.LOCK.release()
                except:
                    pass

        return _wrapper

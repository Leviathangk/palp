"""
    spider 检查工具
    用于在请求前进行检查，并进行等待或停止，防止目标网站崩溃等引起的问题

    参数：
        check_time：检查的频率，默认 3s
        failed_limit：检查的容错，默认 3 次，连续 3 次就执行对应函数

    使用方式：
        class Checker(palp.Checker):
            @classmethod
            def need_stop(cls) -> bool:
                return True # 何时需要停止

        class CheckRequestMiddleware(palp.RequestMiddleware):
            def request_in(self, spider, request) -> None:
                Checker.check_time = 3  # 多少 s 检查一次
                Checker.failed_limit = 3    # 连续多少次就执行 wait、stop

                Checker.check_and_wait()    # 当连续错误达到 failed_limit 在之后执行
                Checker.check_and_stop()    # 当连续错误达到 failed_limit 在之后执行（一旦中断无法挽回，只能重启）
"""
import time
import threading
import traceback

from loguru import logger
from abc import abstractmethod
from palp.spider.spider import Spider


class CheckerBase:
    check_time = 3  # 检查的频率，单位 s
    failed_limit = 3  # 容错，连续几次才执行对应的 wait、stop（大于等于 1 的整数）
    _status_cache = []  # 配和容错缓存最近 failed_limit 次状态
    _last_check_time = None  # 上次检查时间
    _stop_status = False  # 停止信号
    _lock = threading.RLock()  # 线程锁
    _has_stop = False  # 是否已经暂停

    @classmethod
    @abstractmethod
    def need_stop(cls) -> bool:
        """
        判断是否需要停止（只需要返回 true、false）

        :return:
        """

    @classmethod
    def _need_stop(cls) -> bool:
        """
        判断是否需要停止（只需要返回 true、false）

        :return:
        """
        if cls.failed_limit < 1:
            cls.failed_limit = 1

        cls._lock.acquire()
        try:
            now_time = time.time()
            if cls._last_check_time is None or now_time - cls._last_check_time > cls.check_time:
                cls._last_check_time = now_time

                # 缓存最近几次状态
                try:
                    status = bool(cls.need_stop())
                except Exception as e:
                    status = True
                    logger.error("need_stop 错误：{}", e)
                cls._status_cache.append(status)

                # 使得缓存数量和容错一致
                if cls._status_cache and len(cls._status_cache) > cls.failed_limit:
                    del cls._status_cache[:len(cls._status_cache) - cls.failed_limit]

                # 根据容错修改状态
                if cls._status_cache.count(True) >= cls.failed_limit:
                    cls._stop_status = True
                else:
                    cls._stop_status = False

        finally:
            cls._lock.release()

        return cls._stop_status

    @classmethod
    def check_and_wait(cls) -> None:
        """
        判断是否需要暂停所有新请求，需要则等待，直到可以继续才释放
        注意：
            当连续错误达到 failed_limit 在之后执行

        :return:
        """
        cls._lock.acquire()

        try:
            while True:
                if cls._need_stop():
                    logger.warning('当前爬虫已暂停')

                    time.sleep(cls.check_time)
                else:
                    logger.warning('当前爬虫已恢复')
                    break
        finally:
            cls._lock.release()

    @classmethod
    def check_and_stop(cls, spider: Spider) -> None:
        """
        判断是否需要停止爬虫执行（暂停所有新请求，并等待已有请求结束）
        注意：
            当连续错误达到 failed_limit 在之后执行
            一旦中断无法挽回，只能重启

        :param spider: spider
        :return:
        """
        cls._lock.acquire()
        try:
            if cls._need_stop() and not cls._has_stop:
                cls._has_stop = True

                for p in spider.spider_controller_list:
                    p.stop = True

                logger.warning('当前爬虫已停止')
        finally:
            cls._lock.release()


class Checker(CheckerBase):

    @classmethod
    @abstractmethod
    def need_stop(cls) -> bool:
        """
        判断是否需要停止（只需要返回 true、false）

        :return:
        """

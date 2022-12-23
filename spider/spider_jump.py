"""
    jump spider（本地执行，用于处理比较频繁的循环事件）

    注意：
        jump spider 不走 spider 中间件、不走 记录装饰器（request 中间件不影响）
        jump spider 不能 yield item yield 的都不会处理
"""
import time
from abc import abstractmethod
from palp.spider.spider import Spider
from palp.network.request import Request
from palp.controller.controller_spider import SpiderController
from palp.sequence.sequence_memory import PriorityMemorySequence, FIFOMemorySequence


class JumpSpider(Spider):
    """
        jump spider（一般用于实现某个循环，如验证码）
    """

    def __init__(self, request: Request, **kwargs):
        """

        :param request: 最后需要 yield 的请求
        :param kwargs: 需要被 self.xxx 访问到的参数
        """
        super().__init__()

        self.queue = PriorityMemorySequence()  # 请求队列
        self.queue_item = FIFOMemorySequence()  # item 队列
        self.request = request

        # 导入一下自定义设置
        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    def start_requests(self) -> None:
        """
        起始函数

        :return:
        """
        pass

    def start_controller(self) -> None:
        """
        启动 controller

        :return:
        """
        # 启动相应数量的爬虫
        controller = SpiderController(q=self.queue, q_item=self.queue_item, spider=self)
        self.spider_controller_list.append(controller)
        controller.start()

    def wait_spider_controller_done(self) -> None:
        """
        等待线程执行结束

        这里重写是为了避免提示结束，也不用等待自己结束

        :return:
        """
        while True:
            if self.all_spider_controller_is_waiting():
                self.stop_all_spider_controller()
                break
            elif self.all_spider_controller_is_done():
                break

            time.sleep(0.1)  # 不加延迟将会导致性能问题

    def run(self) -> None:
        self.start_controller()  # 任务处理
        self.start_distribute()  # 分发任务
        self.wait_distribute_thread_done()  # 等待任务分发完毕
        self.wait_spider_controller_done()  # 等待自己执行完毕（由于是爬虫中的爬虫，不需要使用装饰器等待）

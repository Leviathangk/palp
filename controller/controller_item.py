"""
    item 流程控制器
"""

from loguru import logger
from palp import settings
from threading import Thread
from palp.item.item import Item
from palp.exception import DropItemException
from palp.tool.short_module import import_module, sort_module


class ItemController(Thread):
    PIPELINE = []
    PIPELINE_CLOSED = False

    def __new__(cls, *args, **kwargs):
        """
        实例化之前加载设置

        :param args:
        :param kwargs:
        """
        if not cls.PIPELINE:
            cls.from_settings()

        return object.__new__(cls)

    def __init__(self, spider, q):
        super().__init__()
        self.spider = spider
        self.queue = q

        self.item_buffer = []
        self.item_buffer_max_size = settings.PIPELINE_ITEM_BUFFER  # item 最大存储数量

    @classmethod
    def from_settings(cls):
        """
        导入设置

        :return:
        """
        modules = sort_module(
            cls_dict=settings.PIPELINE,
            palp_cls_dict=settings.PALP_PIPELINE,
            cls_mapping={
                'ITEM_FILTER_PIPELINE': settings.ITEM_FILTER_PIPELINE[settings.SPIDER_TYPE][settings.FILTERING_MODE]
            }
        )

        cls.PIPELINE = import_module(modules)

    def run(self) -> None:
        """
        item 处理入口

        :return:
        """
        try:
            while True:
                try:
                    if self.spider.spider_done and self.queue.empty():
                        if self.item_buffer:
                            self.pipeline_save()
                        break

                    task = self.queue.get(timeout=1)
                    if task is None:
                        continue

                    # 每个 item 都会先走处理
                    self.pipeline_in(item=task)

                    # 判断是否需要入库
                    if self.item_buffer_max_size == 0 or self.buffer_size >= self.item_buffer_max_size:
                        self.pipeline_save()

                except DropItemException:
                    logger.debug(f"丢弃 item：{self.item_buffer}")
                except Exception as e:
                    # spider 报错处理
                    for middleware in self.spider.SPIDER_MIDDLEWARE:
                        middleware.spider_error(self.spider, e)
        finally:
            if not self.__class__.PIPELINE_CLOSED:
                self.__class__.PIPELINE_CLOSED = True
                self.pipeline_close()

    def pipeline_in(self, item: Item):
        """
        处理清洗等

        :param item:
        :return:
        """
        for pipeline in self.__class__.PIPELINE:
            pipeline.pipeline_in(self.spider, item)

        self.item_buffer.append(item)

    def pipeline_save(self):
        """
        处理入库

        :return:
        """
        # 禁用的话就单条
        if self.item_buffer_max_size == 0 and len(self.item_buffer) != 0:
            item_buffer = self.item_buffer[0]
        else:
            item_buffer = self.item_buffer

        # 入库
        try:
            failed_times = 0
            while failed_times < settings.PIPELINE_RETRY_TIMES:
                try:
                    for pipeline in self.__class__.PIPELINE:
                        pipeline.pipeline_save(self.spider, item_buffer)
                    break
                except DropItemException:
                    raise
                except Exception as e:
                    failed_times += 1

                    for pipeline in self.__class__.PIPELINE:
                        pipeline.pipeline_error(self.spider, item_buffer, e)

                if failed_times >= settings.PIPELINE_RETRY_TIMES:
                    for pipeline in self.__class__.PIPELINE:
                        pipeline.pipeline_failed(self.spider, item_buffer)
                    return
        finally:
            self.item_buffer.clear()

    def pipeline_close(self):
        """
        spider 结束时执行

        :return:
        """
        for pipeline in self.__class__.PIPELINE:
            try:
                pipeline.pipeline_close(self.spider)
            except Exception as e:
                logger.exception(e)

    @property
    def buffer_size(self):
        """
        buffer 大小

        :return:
        """
        return len(self.item_buffer)

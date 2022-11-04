"""
    处理 item
"""
import traceback
from loguru import logger
from palp import settings
from palp.exception import exception_drop
from palp.item.item_base import BaseItem
from palp.tool.short_module import import_module
from palp.buffer.buffer_base import BaseItemBuffer


class ItemBuffer(BaseItemBuffer):
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
        item_filter_pipeline = import_module(
            settings.ITEM_FILTER_PIPELINE[settings.SPIDER_TYPE][settings.FILTERING_MODE])
        cls.PIPELINE = item_filter_pipeline + import_module(settings.PIPELINE)

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

                    task = self.queue.get(timeout=5)
                    if not task:
                        continue

                    # 每个 item 都会先走处理
                    self.pipeline_in(item=task)

                    # 判断是否需要入库
                    if self.item_buffer_max_size == 0 or self.buffer_size >= self.item_buffer_max_size:
                        self.pipeline_save()

                except exception_drop.DropItemException:
                    logger.debug(f"丢弃 item：{self.item_buffer}")
                except Exception as e:
                    # spider 报错处理
                    for middleware in self.spider.SPIDER_MIDDLEWARE:
                        middleware.spider_error(self.spider, e.__class__.__name__, traceback.format_exc())
        finally:
            self.pipeline_close()

    def pipeline_in(self, item: BaseItem):
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
                except exception_drop.DropItemException:
                    raise
                except Exception as e:
                    failed_times += 1

                    for pipeline in self.__class__.PIPELINE:
                        pipeline.pipeline_error(self.spider, item_buffer, e.__class__.__name__, traceback.format_exc())

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
            pipeline.pipeline_close(self.spider)

    @property
    def buffer_size(self):
        """
        buffer 大小

        :return:
        """
        return len(self.item_buffer)

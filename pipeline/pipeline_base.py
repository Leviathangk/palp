"""
    pipeline
"""
from loguru import logger
from typing import Union, List
from palp.item.item_base import BaseItem
from palp.spider.spider_base import BaseSpider


class BasePipeline:
    def pipeline_in(self, spider: BaseSpider, item: BaseItem) -> None:
        """
        入库之前的操作

        :param spider:
        :param item:
        :return:
        """
        pass

    def pipeline_save(self, spider: BaseSpider, item: Union[BaseItem, List[BaseItem]]) -> None:
        """
        入库

        :param spider:
        :param item: 启用 item_buffer 将会是 List[item] 反之为 item
        :return:
        """
        pass

    def pipeline_error(self, spider: BaseSpider, item: Union[BaseItem, List[BaseItem]], exception_type: str,
                       exception: str) -> None:
        """
        入库出错时的操作

        :param spider:
        :param item: 启用 item buffer 时是 List[item]
        :param exception_type: 错误的类型
        :param exception: 错误的详细信息
        :return:
        """
        logger.error(exception)

    def pipeline_failed(self, spider: BaseSpider, item: Union[BaseItem, List[BaseItem]]) -> None:
        """
        超过最大重试次数时的操作

        :param spider:
        :param item: 启用 item buffer 时是 List[item]
        :return:
        """
        logger.warning(f"失败的 item：{item}")

    def pipeline_close(self, spider: BaseSpider) -> None:
        """
        spider 结束时的操作

        :param spider:
        :return:
        """
        pass


# 用于外部引用，避免写类型
class Pipeline(BasePipeline):
    def pipeline_in(self, spider, item) -> None:
        """
        入库之前的操作

        :param spider:
        :param item:
        :return:
        """
        pass

    def pipeline_save(self, spider, item) -> None:
        """
        入库

        :param spider:
        :param item: 启用 item_buffer 将会是 List[item] 反之为 item
        :return:
        """
        pass

    def pipeline_error(self, spider, item, exception_type: str, exception: str) -> None:
        """
        入库出错时的操作

        :param spider:
        :param item: 启用 item buffer 时是 List[item]
        :param exception_type: 错误的类型
        :param exception: 错误的详细信息
        :return:
        """
        pass

    def pipeline_failed(self, spider, item) -> None:
        """
        超过最大重试次数时的操作

        :param spider:
        :param item: 启用 item buffer 时是 List[item]
        :return:
        """
        pass

    def pipeline_close(self, spider) -> None:
        """
        spider 结束时的操作

        :param spider:
        :return:
        """
        pass

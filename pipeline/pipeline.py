"""
    pipeline
"""
from typing import Union, List
from palp.item.item import Item
from palp.spider.spider import SpiderBase


class PipelineBase:
    """
        pipeline 基类
    """

    def pipeline_in(self, spider: SpiderBase, item: Item) -> None:
        """
        入库之前的操作

        :param spider:
        :param item:
        :return:
        """

    def pipeline_save(self, spider: SpiderBase, item: Union[Item, List[Item]]) -> None:
        """
        入库

        :param spider:
        :param item: 启用 item_buffer 将会是 List[item]
        :return:
        """

    def pipeline_error(self, spider: SpiderBase, item: Union[Item, List[Item]], exception: Exception) -> None:
        """
        入库出错时的操作

        :param spider:
        :param item: 启用 item buffer 时是 List[item]
        :param exception: 错误
        :return:
        """

    def pipeline_failed(self, spider: SpiderBase, item: Union[Item, List[Item]]) -> None:
        """
        超过最大重试次数时的操作

        :param spider:
        :param item: 启用 item buffer 时是 List[item]
        :return:
        """

    def pipeline_close(self, spider: SpiderBase) -> None:
        """
        spider 结束时的操作

        :param spider:
        :return:
        """


class Pipeline(PipelineBase):
    """
        用于外部引用：pipeline
    """

    def pipeline_in(self, spider, item) -> None:
        """
        入库之前的操作

        :param spider:
        :param item:
        :return:
        """

    def pipeline_save(self, spider, item) -> None:
        """
        入库

        :param spider:
        :param item: 启用 item_buffer 将会是 List[item] 反之为 item
        :return:
        """

    def pipeline_error(self, spider, item, exception: Exception) -> None:
        """
        入库出错时的操作

        :param spider:
        :param item: 启用 item buffer 时是 List[item]
        :param exception: 错误
        :return:
        """

    def pipeline_failed(self, spider, item) -> None:
        """
        超过最大重试次数时的操作

        :param spider:
        :param item: 启用 item buffer 时是 List[item]
        :return:
        """

    def pipeline_close(self, spider) -> None:
        """
        spider 结束时的操作

        :param spider:
        :return:
        """

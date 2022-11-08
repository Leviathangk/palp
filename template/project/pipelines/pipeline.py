"""
    处理 item，清洗、入库
"""
import palp
from loguru import logger


class Pipeline(palp.Pipeline):
    def pipeline_in(self, spider, item) -> None:
        """
        入库之前的操作，一般是清洗

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
        logger.info(item)

    def pipeline_error(self, spider, item, exception_type: str, exception: str) -> None:
        """
        入库出错时的操作

        :param spider:
        :param item: 启用 item buffer 时是 List[item]
        :param exception_type: 错误的类型
        :param exception: 错误的详细信息
        :return:
        """
        logger.error(exception)

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

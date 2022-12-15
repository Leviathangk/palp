"""
    Pipeline 处理 item，清洗、入库

    注意：默认报错是 logger.error 输出，需要详细信息请使用 logger.exception（输出会很多，但很细）
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

    def pipeline_save(self, spider, item) -> None:
        """
        入库

        :param spider:
        :param item: 启用 item_buffer 将会是 List[item] 反之为 item
        :return:
        """
        logger.info(item)

    def pipeline_error(self, spider, item, exception: Exception) -> None:
        """
        入库出错时的操作

        :param spider:
        :param item: 启用 item buffer 时是 List[item]
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
        logger.warning(f"失败的 item：{item}")

    def pipeline_close(self, spider) -> None:
        """
        spider 结束时的操作，虽然是多线程，但是只会执行一次

        :param spider:
        :return:
        """

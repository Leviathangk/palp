"""
    以进程方式启动指定数量个爬虫实例
"""
from loguru import logger
from multiprocessing import Process
from palp.spider.spider_base import BaseSpider
from palp.tool.short_module import find_spiders_class


# 启动指定 spider
class SpiderRunner(Process):
    def __init__(self, spider: BaseSpider, count: int = 1, **kwargs):
        """

        :param spider:
        :param count: 要运行的数量
        :param kwargs:
        """
        super().__init__()
        self.spider = spider
        self.count = count
        self.kwargs = kwargs

    def run(self) -> None:
        for _ in range(self.count):
            Process(target=self.runner, args=(self.spider, self.kwargs)).start()

    @staticmethod
    def runner(*args):
        spider = args[0]
        spider(**args[1]).start()


def execute(spider_name: str, count: int = 1, **kwargs):
    """
    启动爬虫进程

    :param spider_name: 爬虫名字
    :param count: 启动几个实例
    :param kwargs: 爬虫启动参数
    :return:
    """
    spider_modules = find_spiders_class()

    if spider_name not in spider_modules:
        logger.error(f'无当前 spider，请检查 {spider_name} 是否存在')
        return

    SpiderRunner(spider=spider_modules[spider_name], count=count, **kwargs).start()

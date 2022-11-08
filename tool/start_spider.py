"""
    以进程方式启动指定数量个爬虫实例
"""
import importlib
from pathlib import Path
from loguru import logger
from multiprocessing import Process
from palp.spider.spider_base import BaseSpider


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


def load_spider() -> dict:
    """
    获取所有 spider 实例

    :return:
    """
    path = Path('.').absolute().parent

    # 获取到 spider 的目录
    spider_dir = None
    for i in path.iterdir():
        if i.is_dir() and i.name.lower().startswith('spider'):
            spider_dir = i
            break

    # 获取所有 spider
    spider_modules = {}
    if spider_dir:
        for spider_file in spider_dir.iterdir():
            if spider_file.name.startswith('_'):
                continue
            spider_path = f"{spider_dir.name}.{spider_file.name.split('.')[0]}"
            spider_module = importlib.import_module(spider_path)

            # 获取 spider 的信息
            for key, value in spider_module.__dict__.items():
                if key.startswith('_'):
                    continue
                elif value.__dict__.get('__module__') == spider_path:
                    spider_modules[value.__dict__.get('spider_name')] = value
                    break
    else:
        logger.warning('未找到 spider 文件夹，请将该文件放在与 settings 同级目录')

    return spider_modules


def execute(spider_name: str, count: int = 1, **kwargs):
    """
    启动爬虫进程

    :param spider_name: 爬虫名字
    :param count: 启动几个实例
    :param kwargs: 爬虫启动参数
    :return:
    """
    spider_modules = load_spider()

    if spider_name not in spider_modules:
        logger.error(f'无当前 spider，请检查 {spider_name} 是否存在')
        return

    SpiderRunner(spider=spider_modules[spider_name], count=count, **kwargs).start()

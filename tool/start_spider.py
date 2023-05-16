"""
    以进程方式启动指定数量个爬虫实例
"""
import importlib
import sys
from pathlib import Path
from loguru import logger
from multiprocessing import Process
from palp.spider.spider import Spider
from palp.exception import SpiderHasExistsError


# 启动指定 spider
class SpiderRunner(Process):
    def __init__(self, spider: Spider, count: int = 1, **kwargs):
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
    path = Path(sys.argv[0]).parent.absolute()

    # 获取到 spider 的目录
    spider_dir = None
    for i in path.iterdir():
        if i.is_dir() and i.name == 'spiders':
            spider_dir = i
            break

    # 获取所有 spider
    spider_modules = {}
    if spider_dir:
        for spider_file in spider_dir.iterdir():
            if spider_file.name.startswith('_') or not spider_file.name.endswith('.py'):
                continue

            # Demo.spiders 时
            if spider_dir.parent == path:
                spider_path = f"{spider_dir.name}.{spider_file.name.split('.')[0]}"

            # xxx.xxx.Demo.spiders 时
            else:
                spider_path = f"{spider_dir.parent.name}.{spider_dir.name}.{spider_file.name.split('.')[0]}"

            spider_module = importlib.import_module(spider_path)

            # 获取 spider 的信息
            for value in spider_module.__dict__.values():
                # 判断是未实例化的类，且父类有 Spider
                if issubclass(type(value), type) and issubclass(value, Spider):
                    # 重复报错
                    spider_name = value.spider_name
                    if spider_name in spider_modules:
                        raise SpiderHasExistsError(f'{spider_name} 存在多个！')
                    spider_modules[spider_name] = value
                    break
    else:
        logger.warning('未找到 spiders 文件夹，请将该文件放在与 settings 同级目录')

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

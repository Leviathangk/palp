"""
    创建 spider 文件
"""
import re
import datetime
from pathlib import Path
from typing import Union
from palp.exception import SpiderHasExistsError


class CreateSpider:
    def __init__(self, spider_name: str, spider_type: int = 1):
        """

        :param spider_name: spider 名字
        :param spider_type: spider 类型（1 为普通 spider，2 为分布式 spider）
        """
        self.spider_name = spider_name
        self.spider_type = spider_type
        self.path = Path('.').absolute()  # 相对路径
        self.path_template = Path(__file__).absolute().parent.parent.joinpath('template').joinpath('spider')  # 模板路径
        if self.spider_type == 2:
            self.path_template_spider = self.path_template.joinpath('spider_distributive.tmpl')
        elif self.spider_type == 3:
            self.path_template_spider = self.path_template.joinpath('spider_cycle.tmpl')
        elif self.spider_type == 4:
            if not spider_name.lower().endswith('jump'):
                self.spider_name += '_jump'
            self.path_template_spider = self.path_template.joinpath('spider_jump.tmpl')
        else:
            self.path_template_spider = self.path_template.joinpath('spider_local.tmpl')

    def create(self):
        """
        创建 spider.py

        :return:
        """
        self.check_name()

        spider_dir = self.find_path(path=self.path)
        if not spider_dir:
            spider_dir = self.path

        if spider_dir.joinpath(self.spider_name.lower() + '.py').exists():
            raise SpiderHasExistsError(f'{self.spider_name.lower()} 已存在！')

        with open(self.path_template_spider, 'r', encoding='utf-8') as f:
            content = f.read()

        if self.spider_type == 4:
            spider_name = self.spider_name.replace('_jump', '')
            content = content.replace('${SPIDER_NAME}', spider_name.title())
        else:
            content = content.replace('${SPIDER_NAME}', self.spider_name.title())
        content = content.replace('${SPIDER_NAME_LOWER}', self.spider_name.lower())
        content = content.replace('${DATE}', str(datetime.datetime.now()))

        with open(spider_dir.joinpath(self.spider_name.lower() + '.py'), 'w', encoding='utf-8') as f:
            f.write(content)

    def check_name(self):
        """
        检查名字是否符合要求

        :return:
        """
        matcher = re.match(r'[0-9a-zA-Z_]+', self.spider_name)

        if not re.match(r'[0-9_]', self.spider_name) and matcher and len(matcher.group()) == len(self.spider_name):
            return True

        raise NameError('Spider 名字请以字母开头，并仅含有数字字母下划线！')

    def find_path(self, path: Path, deep: int = 0) -> Union[Path, None]:
        """
        寻找 spiders 文件夹的位置

        :param path:
        :param deep: 递归深度
        :return:
        """
        if deep > 3:
            return

        if path.is_dir() and path.name == 'spiders':
            return path

        for spider_dir in path.iterdir():
            if spider_dir.is_dir():
                spider_dir = self.find_path(spider_dir, deep=deep + 1)
                if spider_dir:
                    return spider_dir


if __name__ == '__main__':
    CreateSpider(spider_name='demo', spider_type=1).create()

"""
    创建 spider 文件
"""
import re
import datetime
from pathlib import Path


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
            self.path_template_spider = self.path_template.joinpath('distributive_spider.tmpl')
        else:
            self.path_template_spider = self.path_template.joinpath('spider.tmpl')

    def create(self):
        """
        创建 spider.py

        :return:
        """
        self.check_name()

        with open(self.path_template_spider, 'r', encoding='utf-8') as f:
            content = f.read()

        content = content.replace('${SPIDER_NAME}', self.spider_name.title())
        content = content.replace('${SPIDER_NAME_LOWER}', self.spider_name.lower())
        content = content.replace('${DATE}', str(datetime.datetime.now()))

        with open(self.path.joinpath(self.spider_name.lower() + '.py'), 'w', encoding='utf-8') as f:
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


if __name__ == '__main__':
    CreateSpider(spider_name='demo', spider_type=1).create()

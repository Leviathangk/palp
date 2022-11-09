"""
    创建 palp 项目
"""
import re
import shutil
from pathlib import Path


class CreateProject:
    def __init__(self, project_name: str):
        """

        :param project_name: 项目名字
        """
        self.project_name = project_name
        self.path = Path('.').absolute()  # 相对路径
        self.path_template = Path(__file__).absolute().parent.parent.joinpath('template').joinpath('project')  # 模板路径

    def create(self):
        """
        复制项目文件

        :return:
        """
        self.check_name()

        parent_path = self.path.joinpath(self.project_name.title())

        if parent_path.exists():
            raise FileExistsError(f'{parent_path} 已存在！')

        shutil.copytree(self.path_template, parent_path)

    def check_name(self):
        """
        检查名字是否符合要求

        :return:
        """
        matcher = re.match(r'[0-9a-zA-Z_]+', self.project_name)

        if not re.match(r'[0-9_]', self.project_name) and matcher and len(matcher.group()) == len(self.project_name):
            return True

        raise NameError('Palp 项目名字请以字母开头，并仅含有数字字母下划线！')


if __name__ == '__main__':
    CreateProject(project_name='demo').create()

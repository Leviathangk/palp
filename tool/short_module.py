import importlib
from pathlib import Path
from typing import Union
from loguru import logger


def import_module(cls_list: Union[list, str]) -> list:
    """
    根据字符串导入模块

    :param cls_list: 设置里面导入的对象
    :return:
    """
    class_name_list = []

    if isinstance(cls_list, str):
        cls_list = [cls_list]

    for cls_info in cls_list:
        module, class_name = cls_info.rsplit(".", 1)  # 就是分割成 from module import class_name
        logger.debug(f"正在从 {module} 导入模块：{class_name}")
        cls = importlib.import_module(module).__getattribute__(class_name)  # 导入
        instance = cls()  # 这里是实例化
        class_name_list.append(instance)

    return class_name_list


def find_spiders_path(path: Path) -> Path:
    """
    寻找 spiders 文件夹的位置

    :param path:
    :return:
    """
    if path.is_dir() and path.name == 'spiders':
        return path

    for spider_dir in path.iterdir():
        if spider_dir.is_dir():
            spider_dir = find_spiders_path(spider_dir)
            if spider_dir:
                return spider_dir


def find_spiders_class() -> dict:
    """
    获取所有 spider 实例

    :return:
    """
    path = Path('.').absolute()

    # 获取到 spider 的目录
    spider_dir = find_spiders_path(path)

    # 获取所有 spider
    spider_modules = {}
    if spider_dir:
        for spider_file in spider_dir.iterdir():
            if spider_file.name.startswith('_'):
                continue

            # Demo.spiders 时
            if spider_dir.parent == path:
                spider_path = f"{spider_dir.name}.{spider_file.name.split('.')[0]}"

            # xxx.xxx.Demo.spiders 时
            else:
                spider_path = f"{spider_dir.parent.name}.{spider_dir.name}.{spider_file.name.split('.')[0]}"

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

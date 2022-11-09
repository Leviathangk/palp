import importlib
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

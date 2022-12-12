"""
    小模块
"""
import importlib
from copy import deepcopy
from loguru import logger
from palp import settings
from typing import Union, Dict, Any


def import_module(cls_list: Union[list, str], instantiate: bool = True) -> list:
    """
    根据字符串导入模块

    :param cls_list: 设置里面导入的对象
    :param instantiate: 是否需要直接实例化，默认实例化
    :return:
    """
    class_name_list = []

    if isinstance(cls_list, str):
        cls_list = [cls_list]

    for cls_info in cls_list:
        module, class_name = cls_info.rsplit(".", 1)  # 就是分割成 from module import class_name
        logger.debug(f"正在从 {module} 导入模块：{class_name}")
        cls = importlib.import_module(module).__getattribute__(class_name)  # 导入
        if instantiate:
            instance = cls()  # 这里是实例化
            class_name_list.append(instance)
        else:
            class_name_list.append(cls)

    return class_name_list


def sort_module_helper(cls_dict: Dict[int, str]) -> list:
    """
    对要导入的模块进行排序

    :param cls_dict:
    :return:
    """
    module_list = []

    for index in sorted([i for i in cls_dict.keys() if isinstance(i, int)]):
        module_list.append(cls_dict[index])

    return module_list


def sort_module(
        cls_dict: Dict[int, str],
        palp_cls_dict: Dict[str, Dict[Any, Any]] = None,
        cls_mapping: Dict[str, str] = None
) -> list:
    """
    对要导入的模块进行排序

    :param palp_cls_dict: palp_cls_dict 的 设置
    :param cls_dict: settings 原生的设置字典
    :param cls_mapping: 懒加载的一些设置
    :return:
    """
    # 设置最大、最小的序号
    min_index = 0
    max_index = 0
    if palp_cls_dict:
        if cls_dict.keys():
            min_index = min(cls_dict.keys())
            max_index = max(cls_dict.keys())

        # 导入慢加载的设置
        for module, index in deepcopy(palp_cls_dict['min']).items():
            # 懒加载
            if isinstance(module, str) and isinstance(index, int) and module in cls_mapping:
                palp_cls_dict['min'][index] = cls_mapping[module]
                del palp_cls_dict['min'][module]

            # 条件判断加载
            elif isinstance(index, list) and hasattr(settings, index[0]):
                if getattr(settings, index[0]):
                    palp_cls_dict['min'][module] = index[1]
                else:
                    del palp_cls_dict['min'][module]

        for module, index in deepcopy(palp_cls_dict['max']).items():
            # 懒加载
            if isinstance(module, str) and isinstance(index, int) and module in cls_mapping:
                palp_cls_dict['max'][index] = cls_mapping[module]
                del palp_cls_dict['max'][module]

            # 条件判断加载
            elif isinstance(index, list) and hasattr(settings, index[0]):
                if getattr(settings, index[0]):
                    palp_cls_dict['max'][module] = index[1]
                else:
                    del palp_cls_dict['max'][module]

        # 获取需要排在最前面的模块，并建立索引
        palp_cls_dict_min_modules = sort_module_helper(palp_cls_dict['min'])
        palp_cls_dict_min_modules_length = len(palp_cls_dict_min_modules)
        for index, palp_cls_dict_min_module in enumerate(palp_cls_dict_min_modules):
            cls_dict[min_index - palp_cls_dict_min_modules_length + index] = palp_cls_dict_min_module

        # 获取需要排在最后面的模块，并建立索引
        palp_cls_dict_min_modules = sort_module_helper(palp_cls_dict['max'])
        for index, palp_cls_dict_min_module in enumerate(palp_cls_dict_min_modules):
            cls_dict[max_index + index + 1] = palp_cls_dict_min_module

    # 模块排序、并创建成列表
    return sort_module_helper(cls_dict)

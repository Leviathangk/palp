"""
    抛出错误
"""


class NotGeneratorFunctionError(Exception):
    """
        函数是含有 yield 的函数
    """

    def __init__(self, *args):
        super(NotGeneratorFunctionError, self).__init__(*args)


class SpiderHasExistsError(Exception):
    """
        spider 已存在错误
    """

    def __init__(self, *args):
        super(SpiderHasExistsError, self).__init__(*args)


class DropRequestException(Exception):
    """
        丢弃请求
    """

    def __init__(self, *args):
        super(DropRequestException, self).__init__(*args)


class DropItemException(Exception):
    """
        丢弃 item
    """

    def __init__(self, *args):
        super(DropItemException, self).__init__(*args)

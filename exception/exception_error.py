"""
    用来抛出错误
"""


# 函数不含有 yield
class NotGeneratorFunctionError(Exception):
    def __init__(self, *args):
        super(NotGeneratorFunctionError, self).__init__(*args)


# spider 已存在错误
class SpiderHasExistsError(Exception):
    def __init__(self, *args):
        super(SpiderHasExistsError, self).__init__(*args)

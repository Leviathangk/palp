"""
    用来抛出错误
"""


# 函数不含有 yield
class NotGeneratorFunctionError(Exception):
    def __init__(self, *args):
        super(NotGeneratorFunctionError, self).__init__(*args)

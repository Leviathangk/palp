"""
    这里是丢弃错误，用来抛掉不要的数据
"""


# 异常：丢弃请求
class DropRequestException(Exception):
    def __init__(self, *args):
        super(DropRequestException, self).__init__(*args)


# 异常：丢弃 item
class DropItemException(Exception):
    def __init__(self, *args):
        super(DropItemException, self).__init__(*args)

from palp.network.request import Request


class RequestGet(Request):
    def __init__(self, **kwargs):
        kwargs.update({'method': 'GET'})
        super().__init__(**kwargs)


class RequestPost(Request):
    def __init__(self, **kwargs):
        kwargs.update({'method': 'POST'})
        super().__init__(**kwargs)


class RequestOptions(Request):
    def __init__(self, **kwargs):
        kwargs.update({'method': 'OPTIONS'})
        super().__init__(**kwargs)


class RequestHead(Request):
    def __init__(self, **kwargs):
        kwargs.update({'method': 'HEAD'})
        super().__init__(**kwargs)


class RequestPatch(Request):
    def __init__(self, **kwargs):
        kwargs.update({'method': 'PATCH'})
        super().__init__(**kwargs)


class RequestDelete(Request):
    def __init__(self, **kwargs):
        kwargs.update({'method': 'DELETE'})
        super().__init__(**kwargs)


if __name__ == '__main__':
    response = RequestGet(url='https://www.baidu.com', titan_meta={'name': '张三'}).send()
    print(response.text)
    print(response.titan)
    print(response.titan_meta)

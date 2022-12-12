from palp.network.request import Request


class RequestGet(Request):
    def __init__(self, url, **kwargs):
        kwargs.update({'url': url, 'method': 'GET'})
        super().__init__(**kwargs)


class RequestPost(Request):
    def __init__(self, url, **kwargs):
        kwargs.update({'url': url, 'method': 'POST'})
        super().__init__(**kwargs)


class RequestOptions(Request):
    def __init__(self, url, **kwargs):
        kwargs.update({'url': url, 'method': 'OPTIONS'})
        super().__init__(**kwargs)


class RequestHead(Request):
    def __init__(self, url, **kwargs):
        kwargs.update({'url': url, 'method': 'HEAD'})
        super().__init__(**kwargs)


class RequestPatch(Request):
    def __init__(self, url, **kwargs):
        kwargs.update({'url': url, 'method': 'PATCH'})
        super().__init__(**kwargs)


class RequestDelete(Request):
    def __init__(self, url, **kwargs):
        kwargs.update({'url': url, 'method': 'DELETE'})
        super().__init__(**kwargs)

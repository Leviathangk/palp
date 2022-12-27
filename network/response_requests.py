"""
    适用于 requests 的响应解析器
"""
from palp.network.response import Response


class RequestsResponse(Response):
    """
        适用于 requests 的响应解析器
    """

    def __init__(self, resp):
        super().__init__(resp)

    @property
    def text(self) -> str:
        return self.content.decode(self.encoding) if self.content is not None else ''

    @property
    def content(self) -> bytes:
        return self.response.content

    def json(self, **kwargs) -> dict:
        return self.response.json(**kwargs)

    @property
    def status_code(self) -> int:
        return self.response.status_code

    @property
    def cookies(self) -> dict:
        return self.response.cookies.get_dict()

    @property
    def headers(self) -> dict:
        return dict(self.response.headers)

    @property
    def url(self) -> str:
        return self.response.url

    @property
    def history(self) -> list:
        """
        响应 url

        :return:
        """
        return self.response.history

    @property
    def links(self):
        """

        :return:
        """
        return self.response.links

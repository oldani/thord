from http import HTTPStatus
from json import dumps
from wsgiref.headers import Headers as _Headers
from thord.types import Union, Send


class Headers(_Headers):
    def items(self):
        """ Overwrite items to return headers as bytes instead of str. """
        return [(k.encode(), v.encode()) for k, v in self._headers]


class Response:
    __slots__ = ["status_code", "content", "headers"]
    media_type = "application/json"
    charset = "utf-8"

    def __init__(
        self, content: Union[str, dict, list, tuple], status_code: int = 200
    ) -> None:
        """ Setup response object, initialize headers. """
        self.status_code: int = HTTPStatus(status_code)

        try:
            self.content: bytes = dumps(content).encode()
        except TypeError:
            raise ValueError("Response content must be JSON serializable")

        self.headers: Headers = Headers()
        self.headers.add_header(
            "content-type", f"{self.media_type}; charset={self.charset}"
        )
        self.headers.add_header("content-length", str(len(self.content)))

    async def __call__(self, send: Send) -> None:
        """ Initialize and send response. """
        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": self.headers.items(),
            }
        )

        await send({"type": "http.response.body", "body": self.content})

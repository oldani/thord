from json import loads
from thord.types import Scope, Receive, AsyncIterable


class Request:
    __slots__ = ["__scope", "__receive", "_stream_consumed", "_body"]

    def __init__(self, scope: Scope, receive: Receive) -> None:
        self.__scope = scope
        self.__receive = receive

        self._stream_consumed: bool = False

    @property
    def method(self) -> str:
        return self.__scope["method"].lower()

    @property
    def schema(self) -> str:
        return self.__scope["scheme"]

    @property
    async def stream(self) -> AsyncIterable[bytes]:
        """ Yield chucks from the body of a request. """
        if hasattr(self, "_body"):
            yield self._body
            return

        if self._stream_consumed:
            raise RuntimeError("Request stream consumed")

        self._stream_consumed = True
        while True:
            message: dict = await self.__receive()

            if message["type"] == "http.request":
                yield message.get("body", b"")

                if not message.get("more_body"):
                    break
            elif message["type"] == "http.disconnect":
                raise RuntimeError("Client Disconnect")

    @property
    async def body(self) -> bytes:
        """ Read request.stream into buffer and return it. """
        if not hasattr(self, "_body"):
            body: bytes = b""

            async for chunk in self.stream:
                body += chunk

            self._body: bytes = body
        return self._body

    @property
    async def json(self) -> dict:
        """ """
        return loads((await self.body).decode("utf-8"))

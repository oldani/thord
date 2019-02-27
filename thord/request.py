from json import loads
from urllib.parse import parse_qs, urlparse
from thord.types import Scope, Receive, AsyncIterable, Any


class QueryArgs(dict):
    def __init__(self, query_string: str) -> None:
        """ Parse query string and pass it to dict class. """
        super().__init__(parse_qs(query_string))

    def get(self, key: str, default=None) -> Any:
        """ Return first value for a given key. """
        try:
            return self[key][0]
        except KeyError:
            return default

    def get_list(self, key: str, default=[]) -> list:
        """ For a given key return a list with all the values
            associated with it. """
        try:
            return self[key]
        except KeyError:
            return default


class URL:
    def __init__(self, scope: Scope, query_string: str) -> None:
        path: str = f"{scope['root_path']}{scope['path']}"
        self._url: str = (
            f"{scope['scheme']}://{scope['server'][0]}:{scope['server'][1]}"
            f"{path}?{query_string}"
        )
        self.url = urlparse(self._url)

    def __repr__(self) -> str:
        return f"URL({self._url})"

    def __eq__(self, value) -> bool:
        return self._url == str(value)

    def __getattr__(self, name: str) -> str:
        return getattr(self.url, name)


class Request:
    __slots__ = ["__scope", "__receive", "_stream_consumed", "_body", "args", "url"]

    def __init__(self, scope: Scope, receive: Receive) -> None:
        self.__scope = scope
        self.__receive = receive

        query_string: str = scope["query_string"].decode()
        self.args: QueryArgs = QueryArgs(query_string)
        self.url: URL = URL(scope, query_string)

        self._stream_consumed: bool = False

    @property
    def method(self) -> str:
        return self.__scope["method"].lower()

    @property
    def scheme(self) -> str:
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

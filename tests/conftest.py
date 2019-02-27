import pytest

from thord.request import Request


@pytest.fixture
def scope():
    return {
        "type": "http",
        "http_version": "1.1",
        "method": "GET",
        "path": "/hello/test",
        "root_path": "",
        "scheme": "http",
        "query_string": b"name=test&n=1&n=2",
        "headers": (
            (b"host", "testserver"),
            (b"user-agent", b"testclient"),
            (b"accept-encoding", b"gzip, deflate"),
            (b"accept", b"*/*"),
            (b"connection", b"keep-alive"),
        ),
        "client": ("testclient", 5000),
        "server": ["testserver", 5001],
    }


@pytest.fixture
def receive():
    body = [
        {"type": "http.request", "body": b'{"say": "hello', "more_body": True},
        {"type": "http.request", "body": b" world!, ", "more_body": True},
        {"type": "http.request", "body": b"this's my API\"}", "more_body": False},
    ]

    async def _receive():
        if _receive.status == len(body) - 1:
            _receive.status = -1
        _receive.status += 1
        return body[_receive.status]

    _receive.status = -1
    return _receive


@pytest.fixture
def request(scope, receive):
    return Request(scope, receive)

import pytest

from thord.request import QueryArgs, URL


def test_queryargs_get():
    query = "name=test&key=value"
    args = QueryArgs(query)

    assert args.get("name") == "test"
    assert args.get("empty") == None


def test_queryargs_get_list():
    query = "name=test1&name=test2&key=value&name=test3"
    args = QueryArgs(query)

    assert args.get_list("name") == ["test1", "test2", "test3"]
    assert args.get_list("empty") == []


def test_url(scope):
    query = scope["query_string"].decode()

    url = URL(scope, query)

    assert url.scheme == "http"
    assert url.path == "/hello/test"
    assert url.query == "name=test&n=1&n=2"


def test_request_method(request):
    assert request.method == "get"


def test_request_scheme(request):
    assert request.scheme == "http"


@pytest.mark.asyncio
async def test_request_stream(request):
    body = b""

    async for chunk in request.stream:
        body += chunk

    assert body == b'{"say": "hello world!, this\'s my API"}'


@pytest.mark.asyncio
async def test_request_stream_consumed(request):
    async for _ in request.stream:
        pass

    with pytest.raises(RuntimeError):
        async for _ in request.stream:
            pass


@pytest.mark.asyncio
async def test_request_body(request):
    await request.body

    body = b""
    async for chunk in request.stream:
        body += chunk
    assert body == b'{"say": "hello world!, this\'s my API"}'


@pytest.mark.asyncio
async def test_request_stream_readed(request):
    assert (await request.body) == b'{"say": "hello world!, this\'s my API"}'


@pytest.mark.asyncio
async def test_request_json(request):
    assert (await request.json) == {"say": "hello world!, this's my API"}

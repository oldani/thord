import pytest


def test_request_method(request):
    assert request.method == "get"


def test_request_schema(request):
    assert request.schema == "http"


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

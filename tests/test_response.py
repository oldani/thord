import pytest
from thord.response import Response


def test_response_invalid_status():
    with pytest.raises(ValueError):
        Response("", status_code=90)


def test_response_invalid_content():
    with pytest.raises(ValueError):
        Response(b"")


@pytest.mark.asyncio
async def test_response_call():
    responses = []

    async def _send(message):
        nonlocal responses
        responses.append(message)

    response = Response({"id": 1, "user": "test"})
    await response(_send)

    assert len(responses) == 2
    assert responses[0] == {
        "type": "http.response.start",
        "status": 200,
        "headers": [
            (b"content-type", b"application/json; charset=utf-8"),
            (b"content-length", b"25"),
        ],
    }


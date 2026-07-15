import httpx
import pytest

from geeko_api.sage_client import SageClient, SageUnavailable


def _client_with_response(status_code: int, json_body: dict | None = None) -> SageClient:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json=json_body or {})

    transport = httpx.MockTransport(handler)
    return SageClient(base_url="http://sage.example", transport=transport)


def _client_that_raises() -> SageClient:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("boom", request=request)

    transport = httpx.MockTransport(handler)
    return SageClient(base_url="http://sage.example", transport=transport)


def test_fetch_fortune_returns_json_on_success():
    client = _client_with_response(200, {"message": "hi", "patched": True})
    result = client.fetch_fortune()
    assert result == {"message": "hi", "patched": True}


def test_fetch_fortune_raises_sage_unavailable_on_http_error():
    client = _client_with_response(500)
    with pytest.raises(SageUnavailable):
        client.fetch_fortune()


def test_fetch_fortune_raises_sage_unavailable_on_connection_error():
    client = _client_that_raises()
    with pytest.raises(SageUnavailable):
        client.fetch_fortune()

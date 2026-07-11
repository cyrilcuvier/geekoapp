import httpx
import pytest

from geeko_api.oracle_client import OracleClient, OracleUnavailable


def _client_with_response(status_code: int, json_body: dict | None = None) -> OracleClient:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json=json_body or {})

    transport = httpx.MockTransport(handler)
    return OracleClient(base_url="http://oracle.example", transport=transport)


def _client_that_raises() -> OracleClient:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("boom", request=request)

    transport = httpx.MockTransport(handler)
    return OracleClient(base_url="http://oracle.example", transport=transport)


def test_fetch_fortune_returns_json_on_success():
    client = _client_with_response(200, {"message": "hi", "patched": True})
    result = client.fetch_fortune()
    assert result == {"message": "hi", "patched": True}


def test_fetch_fortune_raises_oracle_unavailable_on_http_error():
    client = _client_with_response(500)
    with pytest.raises(OracleUnavailable):
        client.fetch_fortune()


def test_fetch_fortune_raises_oracle_unavailable_on_connection_error():
    client = _client_that_raises()
    with pytest.raises(OracleUnavailable):
        client.fetch_fortune()

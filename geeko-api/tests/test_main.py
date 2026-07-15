import fakeredis
from fastapi.testclient import TestClient

from geeko_api.main import create_app
from geeko_api.sage_client import SageUnavailable
from geeko_api.store import GeekoStore


class _RaisingSage:
    def fetch_fortune(self):
        raise SageUnavailable("no sage in session 1")


class _WorkingSage:
    def fetch_fortune(self):
        return {"message": "ca va bien", "patched": True}


def _client(sage=None) -> TestClient:
    store = GeekoStore(fakeredis.FakeRedis())
    app = create_app(store=store, sage_client=sage, tick_seconds=3600)
    return TestClient(app)


def test_healthz():
    response = _client().get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_geeko_endpoint_returns_a_state_even_on_first_call():
    response = _client().get("/api/geeko")
    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"x", "y", "color", "mood", "step"}


def test_sage_endpoint_degrades_gracefully_when_sage_is_none():
    response = _client(sage=None).get("/api/sage")
    assert response.status_code == 200
    assert response.json() == {"available": False}


def test_sage_endpoint_degrades_gracefully_when_sage_raises():
    response = _client(sage=_RaisingSage()).get("/api/sage")
    assert response.status_code == 200
    assert response.json() == {"available": False}


def test_sage_endpoint_returns_fortune_when_available():
    response = _client(sage=_WorkingSage()).get("/api/sage")
    assert response.status_code == 200
    assert response.json() == {"available": True, "message": "ca va bien", "patched": True}

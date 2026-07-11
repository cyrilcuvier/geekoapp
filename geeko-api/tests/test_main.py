import fakeredis
from fastapi.testclient import TestClient

from geeko_api.main import create_app
from geeko_api.oracle_client import OracleUnavailable
from geeko_api.store import GeekoStore


class _RaisingOracle:
    def fetch_fortune(self):
        raise OracleUnavailable("no oracle in session 1")


class _WorkingOracle:
    def fetch_fortune(self):
        return {"message": "ca va bien", "patched": True}


def _client(oracle=None) -> TestClient:
    store = GeekoStore(fakeredis.FakeRedis())
    app = create_app(store=store, oracle_client=oracle, tick_seconds=3600)
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


def test_oracle_endpoint_degrades_gracefully_when_oracle_is_none():
    response = _client(oracle=None).get("/api/oracle")
    assert response.status_code == 200
    assert response.json() == {"available": False}


def test_oracle_endpoint_degrades_gracefully_when_oracle_raises():
    response = _client(oracle=_RaisingOracle()).get("/api/oracle")
    assert response.status_code == 200
    assert response.json() == {"available": False}


def test_oracle_endpoint_returns_fortune_when_available():
    response = _client(oracle=_WorkingOracle()).get("/api/oracle")
    assert response.status_code == 200
    assert response.json() == {"available": True, "message": "ca va bien", "patched": True}

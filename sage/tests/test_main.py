from fastapi.testclient import TestClient

from sage_service.main import create_app


def test_healthz_reports_unpatched_by_default(tmp_path):
    app = create_app(flag_path=tmp_path / "patched")
    client = TestClient(app)
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"patched": False}


def test_healthz_reports_patched_once_flag_exists(tmp_path):
    flag_path = tmp_path / "patched"
    flag_path.write_text("patched")
    app = create_app(flag_path=flag_path)
    client = TestClient(app)
    assert client.get("/healthz").json() == {"patched": True}


def test_fortune_includes_a_message_and_patched_flag(tmp_path):
    app = create_app(flag_path=tmp_path / "patched")
    client = TestClient(app)
    response = client.get("/fortune")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["message"], str) and body["message"]
    assert body["patched"] is False


def test_fortune_is_deterministic_when_unpatched_and_varies_when_patched(tmp_path):
    unpatched_app = create_app(flag_path=tmp_path / "patched")
    client = TestClient(unpatched_app)
    first = client.get("/fortune").json()["message"]
    second = client.get("/fortune").json()["message"]
    assert first == second  # unpatched Sage uses a fixed seed -> same fortune every time

    flag_path = tmp_path / "patched-2"
    flag_path.write_text("patched")
    patched_app = create_app(flag_path=flag_path)
    patched_client = TestClient(patched_app)
    messages = {patched_client.get("/fortune").json()["message"] for _ in range(20)}
    assert len(messages) > 1  # patched Sage uses a real random source -> varies

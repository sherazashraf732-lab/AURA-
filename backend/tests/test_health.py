from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_ok_and_headers() -> None:
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["x-request-id"]


def test_unknown_route_uses_error_schema() -> None:
    r = client.get("/api/v1/does-not-exist")
    assert r.status_code == 404
    body = r.json()["error"]
    assert body["code"] == "http_404"
    assert body["request_id"]

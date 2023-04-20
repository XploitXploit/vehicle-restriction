from fastapi.testclient import TestClient
from app.main import app


def test_health_check():
    client = TestClient(app)
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"db": {"1": 1}, "db_log": {"1": 1}}


def test_health_check_vehicles():
    client = TestClient(app)
    response = client.get("/vehicles/")
    assert response.status_code == 200
    assert response.json()["Status"] == "OK"

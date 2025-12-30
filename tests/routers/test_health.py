from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data["status"] == "healthy"

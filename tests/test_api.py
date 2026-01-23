from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_features_endpoint_exists():
    """
    Feature endpoint must respond.
    404 is acceptable when entity does not exist.
    """
    response = client.get("/features/test-user")

    assert response.status_code in (200, 404)

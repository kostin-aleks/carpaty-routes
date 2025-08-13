"""
test of main end-point
"""
from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)


def test_read_main():
    """
    test of main end-point
    """
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["application"] == "Carpathians winter routes"

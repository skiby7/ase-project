import os
print(os.getenv("PYTHONPATH"))
import pytest
from service.main import app

@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    return TestClient(app)

def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "ok" in response.text

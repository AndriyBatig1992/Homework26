import main
from fastapi.testclient import TestClient

client = TestClient(main.app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200


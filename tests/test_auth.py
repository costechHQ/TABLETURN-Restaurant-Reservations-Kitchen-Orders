from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_register_user():
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "pytest_user_001@example.com",
            "password": "pass@123",
            "role": "diner",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "pytest_user_001@example.com"
    assert data["role"] == "diner"
    assert "id" in data
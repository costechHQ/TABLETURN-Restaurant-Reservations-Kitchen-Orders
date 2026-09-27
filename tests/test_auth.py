from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.main import app
from app.db.database import engine
from app.models.user import User, UserRole


client = TestClient(app)


def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "pytest_user_001@example.com",
            "password": "pass@123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "pytest_user_001@example.com"
    assert data["role"] == "diner"
    assert "id" in data


def test_staff_creation_requires_manager(client):
    response = client.post(
        "/api/v1/auth/staff",
        json={
            "email": "waiter@example.com",
            "password": "pass@123",
            "role": "waiter",
        },
    )

    assert response.status_code == 401


def test_manager_can_create_staff(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "manager@example.com",
            "password": "pass@123",
        },
    )

    with Session(engine) as session:
        user = session.exec(
            select(User).where(
                User.email == "manager@example.com"
            )
        ).first()

        user.role = UserRole.MANAGER
        session.add(user)
        session.commit()

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "manager@example.com",
            "password": "pass@123",
        },
    )

    token = login.json()["access_token"]

    response = client.post(
        "/api/v1/auth/staff",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "email": "waiter@example.com",
            "password": "pass@123",
            "role": "waiter",
        },
    )

    assert response.status_code == 201
    assert response.json()["role"] == "waiter"

    for role in ["kitchen", "manager"]:
        response = client.post(
            "/api/v1/auth/staff",
            headers={
                "Authorization": f"Bearer {token}",
            },
            json={
                "email": f"new_{role}@example.com",
                "password": "pass@123",
                "role": role,
            },
        )

        assert response.status_code == 201
        assert response.json()["role"] == role

def test_diner_cannot_create_staff(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "diner@example.com",
            "password": "pass@123",
        },
    )

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "diner@example.com",
            "password": "pass@123",
        },
    )

    token = login.json()["access_token"]

    response = client.post(
        "/api/v1/auth/staff",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "email": "another_waiter@example.com",
            "password": "pass@123",
            "role": "waiter",
        },
    )

    assert response.status_code == 403
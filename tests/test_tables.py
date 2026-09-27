from app.core.security import hash_password
from app.models.user import User, UserRole


def test_manager_can_create_table(client):
    email = "pytest_manager@example.com"
    password = "TestPassword123!"

    # Create manager directly in the test database
    from app.db.database import engine
    from sqlmodel import Session

    with Session(engine) as session:
        manager = User(
            email=email,
            password_hash=hash_password(password),
            role=UserRole.MANAGER,
        )
        session.add(manager)
        session.commit()

    # Login manager
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    # Create table
    response = client.post(
        "/api/v1/tables",
        json={
            "code": "PYT03",
            "capacity": 4,
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["code"] == "PYT03"
    assert data["capacity"] == 4
    assert "id" in data

def test_diner_cannot_create_table(client):
    email = "pytest_diner@example.com"
    password = "TestPassword123!"

    from app.db.database import engine
    from sqlmodel import Session
    from app.core.security import hash_password
    from app.models.user import User, UserRole

    with Session(engine) as session:
        diner = User(
            email=email,
            password_hash=hash_password(password),
            role=UserRole.DINER,
        )
        session.add(diner)
        session.commit()

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.post(
        "/api/v1/tables",
        json={
            "code": "PYT04",
            "capacity": 4,
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 403



def test_invalid_table_capacity(client):
    email = "pytest_manager@example.com"
    password = "TestPassword123!"

    from app.db.database import engine
    from sqlmodel import Session
    from app.core.security import hash_password
    from app.models.user import User, UserRole

    with Session(engine) as session:
        manager = User(
            email=email,
            password_hash=hash_password(password),
            role=UserRole.MANAGER,
        )
        session.add(manager)
        session.commit()

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.post(
        "/api/v1/tables",
        json={
            "code": "PYT05",
            "capacity": 0,
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 422
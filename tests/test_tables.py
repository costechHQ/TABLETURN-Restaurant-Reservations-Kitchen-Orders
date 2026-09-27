from app.core.security import create_access_token, hash_password
from app.db.database import engine
from app.models.user import User, UserRole
from sqlmodel import Session


def test_manager_can_create_table(client):
    with Session(engine) as session:
        manager = User(
            email="pytest_manager@example.com",
            password_hash=hash_password("TestPassword123!"),
            role=UserRole.MANAGER,
        )

        session.add(manager)
        session.commit()
        session.refresh(manager)

        manager_id = manager.id

    token = create_access_token(
        user_id=manager_id,
        role=UserRole.MANAGER.value,
    )

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
    with Session(engine) as session:
        diner = User(
            email="pytest_diner@example.com",
            password_hash=hash_password("TestPassword123!"),
            role=UserRole.DINER,
        )

        session.add(diner)
        session.commit()
        session.refresh(diner)

        diner_id = diner.id

    token = create_access_token(
        user_id=diner_id,
        role=UserRole.DINER.value,
    )

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
    with Session(engine) as session:
        manager = User(
            email="pytest_invalid_capacity@example.com",
            password_hash=hash_password("TestPassword123!"),
            role=UserRole.MANAGER,
        )

        session.add(manager)
        session.commit()
        session.refresh(manager)

        manager_id = manager.id

    token = create_access_token(
        user_id=manager_id,
        role=UserRole.MANAGER.value,
    )

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

from datetime import datetime, timedelta, timezone

from app.core.security import hash_password
from app.db.database import engine
from app.models.table import RestaurantTable
from app.models.user import User, UserRole
from sqlmodel import Session


def test_diner_can_create_reservation(client):
    email = "pytest_diner@example.com"
    password = "TestPassword123!"

    with Session(engine) as session:
        manager = User(
            email="pytest_manager@example.com",
            password_hash=hash_password(password),
            role=UserRole.MANAGER,
        )

        table = RestaurantTable(
            code="RES01",
            capacity=4,
        )

        diner = User(
            email=email,
            password_hash=hash_password(password),
            role=UserRole.DINER,
        )

        session.add(manager)
        session.add(table)
        session.add(diner)
        session.commit()
        session.refresh(table)
        session.refresh(diner)

        table_id = table.id

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    start = datetime.now(timezone.utc) + timedelta(hours=1)
    end = start + timedelta(hours=1)

    response = client.post(
        "/api/v1/reservations",
        json={
            "table_id": table_id,
            "party_size": 2,
            "start_at": start.isoformat(),
            "end_at": end.isoformat(),
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["table_id"] == table_id
    assert data["diner_id"] == diner.id
    assert data["party_size"] == 2
    assert data["status"] == "confirmed"


def test_overlapping_reservation_is_rejected(client):
    password = "TestPassword123!"

    with Session(engine) as session:
        table = RestaurantTable(
            code="RES02",
            capacity=4,
        )

        diner = User(
            email="pytest_diner_overlap@example.com",
            password_hash=hash_password(password),
            role=UserRole.DINER,
        )

        session.add(table)
        session.add(diner)
        session.commit()
        session.refresh(table)

        table_id = table.id

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "pytest_diner_overlap@example.com",
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    start = datetime.now(timezone.utc) + timedelta(hours=2)
    end = start + timedelta(hours=1)

    first_response = client.post(
        "/api/v1/reservations",
        json={
            "table_id": table_id,
            "party_size": 2,
            "start_at": start.isoformat(),
            "end_at": end.isoformat(),
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert first_response.status_code == 201

    overlapping_response = client.post(
        "/api/v1/reservations",
        json={
            "table_id": table_id,
            "party_size": 2,
            "start_at": (start + timedelta(minutes=30)).isoformat(),
            "end_at": (end + timedelta(minutes=30)).isoformat(),
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert overlapping_response.status_code == 409



def test_back_to_back_reservations_are_allowed(client):
    password = "TestPassword123!"
    email = "pytest_diner_boundary@example.com"

    with Session(engine) as session:
        table = RestaurantTable(
            code="RES03",
            capacity=4,
        )

        diner = User(
            email=email,
            password_hash=hash_password(password),
            role=UserRole.DINER,
        )

        session.add(table)
        session.add(diner)
        session.commit()
        session.refresh(table)

        table_id = table.id

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    start = datetime.now(timezone.utc) + timedelta(hours=4)
    middle = start + timedelta(hours=1)
    end = middle + timedelta(hours=1)

    first_response = client.post(
        "/api/v1/reservations",
        json={
            "table_id": table_id,
            "party_size": 2,
            "start_at": start.isoformat(),
            "end_at": middle.isoformat(),
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/reservations",
        json={
            "table_id": table_id,
            "party_size": 2,
            "start_at": middle.isoformat(),
            "end_at": end.isoformat(),
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert second_response.status_code == 201
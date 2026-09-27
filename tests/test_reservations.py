from datetime import datetime, timedelta, timezone

from app.core.security import hash_password
from app.db.database import engine
from app.models.table import RestaurantTable
from app.models.user import User, UserRole
from sqlmodel import Session
from app.core.security import create_access_token


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


def test_reservation_owner_can_cancel(client):
    password = "TestPassword123!"
    email = "pytest_diner_cancel@example.com"

    with Session(engine) as session:
        table = RestaurantTable(
            code="RES04",
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
        session.refresh(diner)

        table_id = table.id
        diner_id = diner.id

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    start = datetime.now(timezone.utc) + timedelta(hours=5)
    end = start + timedelta(hours=1)

    reservation_response = client.post(
        "/api/v1/reservations",
        json={
            "table_id": table_id,
            "party_size": 2,
            "start_at": start.isoformat(),
            "end_at": end.isoformat(),
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert reservation_response.status_code == 201

    reservation_id = reservation_response.json()["id"]

    cancel_response = client.post(
        f"/api/v1/reservations/{reservation_id}/cancel",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert cancel_response.status_code == 200

    data = cancel_response.json()

    assert data["id"] == reservation_id
    assert data["diner_id"] == diner_id
    assert data["status"] == "cancelled"



def test_waiter_can_cancel_reservation(client):
    password = "TestPassword123!"
    waiter_email = "pytest_waiter_cancel@example.com"
    diner_email = "pytest_diner_waiter_cancel@example.com"

    with Session(engine) as session:
        table = RestaurantTable(code="RES06", capacity=4)

        waiter = User(
            email=waiter_email,
            password_hash=hash_password(password),
            role=UserRole.WAITER,
        )

        diner = User(
            email=diner_email,
            password_hash=hash_password(password),
            role=UserRole.DINER,
        )

        session.add(table)
        session.add(waiter)
        session.add(diner)
        session.commit()

        session.refresh(table)
        session.refresh(waiter)
        session.refresh(diner)

        table_id = table.id
        waiter_id = waiter.id

    diner_login = client.post(
        "/api/v1/auth/login",
        json={
            "email": diner_email,
            "password": password,
        },
    )

    assert diner_login.status_code == 200

    diner_token = diner_login.json()["access_token"]

    start = datetime.now(timezone.utc) + timedelta(hours=5)
    end = start + timedelta(hours=1)

    reservation_response = client.post(
        "/api/v1/reservations",
        json={
            "table_id": table_id,
            "party_size": 2,
            "start_at": start.isoformat(),
            "end_at": end.isoformat(),
        },
        headers={"Authorization": f"Bearer {diner_token}"},
    )

    assert reservation_response.status_code == 201

    reservation_id = reservation_response.json()["id"]

    waiter_token = create_access_token(
        user_id=waiter.id,
        role=UserRole.WAITER.value,
    )

    cancel_response = client.post(
        f"/api/v1/reservations/{reservation_id}/cancel",
        headers={"Authorization": f"Bearer {waiter_token}"},
    )

    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "cancelled"
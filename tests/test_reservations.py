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
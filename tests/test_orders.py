from sqlmodel import Session

from app.core.security import create_access_token, hash_password
from app.db.database import engine
from app.models.table import RestaurantTable
from app.models.user import User, UserRole



def test_waiter_can_create_order(client):
    with Session(engine) as session:
        table = RestaurantTable(
            code="T01",
            capacity=4,
        )

        waiter = User(
            email="pytest_waiter_order@example.com",
            password_hash=hash_password("TestPassword123!"),
            role=UserRole.WAITER,
        )

        session.add(table)
        session.add(waiter)
        session.commit()

        session.refresh(table)
        session.refresh(waiter)

        table_id = table.id
        waiter_id = waiter.id

    token = create_access_token(
        user_id=waiter_id,
        role=UserRole.WAITER.value,
    )

    response = client.post(
        "/api/v1/orders",
        json={
            "table_id": table_id,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201

    data = response.json()

    assert data["table_id"] == table_id
    assert data["waiter_id"] == waiter_id
    assert data["status"] == "placed"
    assert data["ordered_items"] == []
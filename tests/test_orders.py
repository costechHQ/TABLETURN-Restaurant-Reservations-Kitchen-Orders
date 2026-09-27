from sqlmodel import Session

from app.core.security import create_access_token, hash_password
from app.db.database import engine
from app.models.table import RestaurantTable
from app.models.user import User, UserRole

from decimal import Decimal
from app.models.menu_item import MenuItem



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


def test_placed_order_appears_in_kitchen_queue_as_new(client):
    with Session(engine) as session:
        table = RestaurantTable(
            code="T03",
            capacity=4,
        )

        waiter = User(
            email="pytest_waiter_kitchen@example.com",
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
        json={"table_id": table_id},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201

    order_id = response.json()["id"]

    from app.core.firebase import db

    document = db.collection("kitchen_queue").document(str(order_id)).get()

    assert document.exists
    data = document.to_dict()

    assert data["order_id"] == order_id
    assert data["status"] == "NEW"




def test_waiter_can_add_order_item(client):
    with Session(engine) as session:
        table = RestaurantTable(
            code="T02",
            capacity=4,
        )

        waiter = User(
            email="pytest_waiter_item@example.com",
            password_hash=hash_password("TestPassword123!"),
            role=UserRole.WAITER,
        )

        menu_item = MenuItem(
            name="Jollof Rice",
            description="Classic Nigerian jollof rice served with vegetables",
            price=Decimal("2500.00"),
            is_available=True,
        )

        session.add(table)
        session.add(waiter)
        session.add(menu_item)
        session.commit()

        session.refresh(table)
        session.refresh(waiter)
        session.refresh(menu_item)

        table_id = table.id
        waiter_id = waiter.id
        menu_item_id = menu_item.id

    token = create_access_token(
        user_id=waiter_id,
        role=UserRole.WAITER.value,
    )

    order_response = client.post(
        "/api/v1/orders",
        json={
            "table_id": table_id,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert order_response.status_code == 201

    order_id = order_response.json()["id"]

    item_response = client.post(
        f"/api/v1/orders/{order_id}/items",
        json={
            "menu_item_id": menu_item_id,
            "qty": 2,
            "notes": "Extra spicy",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert item_response.status_code == 201

    data = item_response.json()

    assert data["order_id"] == order_id
    assert data["menu_item_id"] == menu_item_id
    assert data["qty"] == 2
    assert Decimal(str(data["unit_price"])) == Decimal("2500.00")
    assert Decimal(str(data["total_price"])) == Decimal("5000.00")


def test_add_item_to_nonexistent_order_returns_404(client):
    with Session(engine) as session:
        menu_item = MenuItem(
            name="Fried Rice",
            description="Nigerian fried rice served with mixed vegetables",
            price=Decimal("3000.00"),
            is_available=True,
        )

        waiter = User(
            email="pytest_waiter_missing_order@example.com",
            password_hash=hash_password("TestPassword123!"),
            role=UserRole.WAITER,
        )

        session.add(menu_item)
        session.add(waiter)
        session.commit()

        session.refresh(menu_item)
        session.refresh(waiter)

        menu_item_id = menu_item.id
        waiter_id = waiter.id

    token = create_access_token(
        user_id=waiter_id,
        role=UserRole.WAITER.value,
    )

    response = client.post(
        "/api/v1/orders/99999/items",
        json={
            "menu_item_id": menu_item_id,
            "qty": 1,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


def test_kitchen_can_move_order_to_preparing(client):
    with Session(engine) as session:
        table = RestaurantTable(
            code="T03",
            capacity=4,
        )

        waiter = User(
            email="pytest_waiter_status@example.com",
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

    waiter_token = create_access_token(
        user_id=waiter_id,
        role=UserRole.WAITER.value,
    )

    order_response = client.post(
        "/api/v1/orders",
        json={"table_id": table_id},
        headers={"Authorization": f"Bearer {waiter_token}"},
    )

    assert order_response.status_code == 201

    order_id = order_response.json()["id"]

    kitchen_token = create_access_token(
        user_id=waiter_id,
        role=UserRole.KITCHEN.value,
    )

    status_response = client.post(
        f"/api/v1/orders/{order_id}/status",
        json={"status": "preparing"},
        headers={"Authorization": f"Bearer {kitchen_token}"},
    )

    assert status_response.status_code == 200
    assert status_response.json()["status"] == "preparing"


def test_reject_invalid_order_status_transition(client):
    with Session(engine) as session:
        table = RestaurantTable(
            code="T04",
            capacity=4,
        )

        waiter = User(
            email="pytest_waiter_invalid_status@example.com",
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

    order_response = client.post(
        "/api/v1/orders",
        json={"table_id": table_id},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert order_response.status_code == 201

    order_id = order_response.json()["id"]

    kitchen_token = create_access_token(
        user_id=waiter_id,
        role=UserRole.KITCHEN.value,
    )

    response = client.post(
        f"/api/v1/orders/{order_id}/status",
        json={"status": "ready"},
        headers={"Authorization": f"Bearer {kitchen_token}"},
    )

    assert response.status_code == 409


def test_kitchen_can_move_order_to_ready(client):
    with Session(engine) as session:
        table = RestaurantTable(
            code="T04",
            capacity=4,
        )

        waiter = User(
            email="pytest_waiter_ready@example.com",
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

    waiter_token = create_access_token(
        user_id=waiter_id,
        role=UserRole.WAITER.value,
    )

    order_response = client.post(
        "/api/v1/orders",
        json={"table_id": table_id},
        headers={"Authorization": f"Bearer {waiter_token}"},
    )

    assert order_response.status_code == 201

    order_id = order_response.json()["id"]

    kitchen_token = create_access_token(
        user_id=waiter_id,
        role=UserRole.KITCHEN.value,
    )

    preparing_response = client.post(
        f"/api/v1/orders/{order_id}/status",
        json={"status": "preparing"},
        headers={"Authorization": f"Bearer {kitchen_token}"},
    )

    assert preparing_response.status_code == 200

    ready_response = client.post(
        f"/api/v1/orders/{order_id}/status",
        json={"status": "ready"},
        headers={"Authorization": f"Bearer {kitchen_token}"},
    )

    assert ready_response.status_code == 200
    assert ready_response.json()["status"] == "ready"


def test_kitchen_can_move_order_to_served(client):
    with Session(engine) as session:
        table = RestaurantTable(
            code="T05",
            capacity=4,
        )

        waiter = User(
            email="pytest_waiter_served@example.com",
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

    waiter_token = create_access_token(
        user_id=waiter_id,
        role=UserRole.WAITER.value,
    )

    order_response = client.post(
        "/api/v1/orders",
        json={"table_id": table_id},
        headers={"Authorization": f"Bearer {waiter_token}"},
    )

    assert order_response.status_code == 201

    order_id = order_response.json()["id"]

    kitchen_token = create_access_token(
        user_id=waiter_id,
        role=UserRole.KITCHEN.value,
    )

    preparing_response = client.post(
        f"/api/v1/orders/{order_id}/status",
        json={"status": "preparing"},
        headers={"Authorization": f"Bearer {kitchen_token}"},
    )

    assert preparing_response.status_code == 200

    ready_response = client.post(
        f"/api/v1/orders/{order_id}/status",
        json={"status": "ready"},
        headers={"Authorization": f"Bearer {kitchen_token}"},
    )

    assert ready_response.status_code == 200

    served_response = client.post(
        f"/api/v1/orders/{order_id}/status",
        json={"status": "served"},
        headers={"Authorization": f"Bearer {kitchen_token}"},
    )

    assert served_response.status_code == 200
    assert served_response.json()["status"] == "served"


def test_waiter_can_create_payment(client):
    with Session(engine) as session:
        table = RestaurantTable(
            code="T06",
            capacity=4,
        )

        waiter = User(
            email="pytest_waiter_payment@example.com",
            password_hash=hash_password("TestPassword123!"),
            role=UserRole.WAITER,
        )

        menu_item = MenuItem(
            name="Chicken Rice",
            description="Rice served with grilled chicken and vegetables",
            price=Decimal("2500.00"),
            is_available=True,
        )

        session.add(table)
        session.add(waiter)
        session.add(menu_item)
        session.commit()

        session.refresh(table)
        session.refresh(waiter)
        session.refresh(menu_item)

        table_id = table.id
        waiter_id = waiter.id
        menu_item_id = menu_item.id

    token = create_access_token(
        user_id=waiter_id,
        role=UserRole.WAITER.value,
    )

    order_response = client.post(
        "/api/v1/orders",
        json={"table_id": table_id},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert order_response.status_code == 201

    order_id = order_response.json()["id"]

    item_response = client.post(
        f"/api/v1/orders/{order_id}/items",
        json={
            "menu_item_id": menu_item_id,
            "qty": 1,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert item_response.status_code == 201

    payment_response = client.post(
        f"/api/v1/orders/{order_id}/payments",
        json={
            "reference": "TEST-PAYMENT-001",
            "method": "cash",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert payment_response.status_code == 201

    data = payment_response.json()

    assert data["order_id"] == order_id
    assert Decimal(str(data["amount"])) == Decimal("2500.00")
    assert data["method"] == "cash"
    assert data["status"] == "pending"
from decimal import Decimal

from sqlmodel import Session

from app.core.security import create_access_token, hash_password
from app.db.database import engine
from app.models.user import User, UserRole


def test_manager_can_create_menu_item(client):
    with Session(engine) as session:
        manager = User(
            email="pytest_menu_manager@example.com",
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
        "/api/v1/menu",
        json={
            "name": "Jollof Rice",
            "description": "Classic Nigerian jollof rice with vegetables",
            "price": "2500.00",
            "is_available": True,
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Jollof Rice"
    assert data["description"] == "Classic Nigerian jollof rice with vegetables"
    assert Decimal(str(data["price"])) == Decimal("2500.00")
    assert data["is_available"] is True


def test_diner_cannot_create_menu_item(client):
    with Session(engine) as session:
        diner = User(
            email="pytest_menu_diner@example.com",
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
        "/api/v1/menu",
        json={
            "name": "Fried Rice",
            "description": "Fried rice with vegetables and scrambled egg",
            "price": "3000.00",
            "is_available": True,
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 403


def test_public_menu_returns_only_available_items(client):
    from decimal import Decimal

    from app.models.menu_item import MenuItem

    with Session(engine) as session:
        available_item = MenuItem(
            name="Available Rice",
            description="Freshly prepared rice with vegetables and sauce",
            price=Decimal("2500.00"),
            is_available=True,
        )

        unavailable_item = MenuItem(
            name="Unavailable Soup",
            description="Soup that is currently unavailable for ordering",
            price=Decimal("2000.00"),
            is_available=False,
        )

        session.add(available_item)
        session.add(unavailable_item)
        session.commit()

    response = client.get("/api/v1/menu")

    assert response.status_code == 200

    data = response.json()

    names = [item["name"] for item in data]

    assert "Available Rice" in names
    assert "Unavailable Soup" not in names


def test_update_nonexistent_menu_item_returns_404(client):
    with Session(engine) as session:
        manager = User(
            email="pytest_menu_update@example.com",
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

    response = client.put(
        "/api/v1/menu/99999",
        json={
            "price": "3500.00",
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Menu item not found"

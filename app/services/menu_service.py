import json
from app.core.redis import redis_client
from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.menu_item import MenuItem
from app.schemas.menu import MenuItemCreate, MenuItemUpdate


def create_menu_item(
    session: Session,
    data: MenuItemCreate,
) -> MenuItem:

    existing_item = session.exec(
        select(MenuItem).where(MenuItem.name == data.name)
    ).first()

    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Menu item already exists",
        )

    menu_item = MenuItem(
        name=data.name,
        description=data.description,
        price=data.price,
        is_available=data.is_available,
    )

    session.add(menu_item)
    session.commit()
    session.refresh(menu_item)
    redis_client.delete("menu:list")

    return menu_item


def update_menu_item(
    session: Session,
    menu_item_id: int,
    data: MenuItemUpdate,
) -> MenuItem:

    menu_item = session.get(MenuItem, menu_item_id)

    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    if data.name is not None:
        menu_item.name = data.name

    if data.description is not None:
        menu_item.description = data.description

    if data.price is not None:
        menu_item.price = data.price

    if data.is_available is not None:
        menu_item.is_available = data.is_available

    session.add(menu_item)
    session.commit()
    session.refresh(menu_item)
    redis_client.delete("menu:list")

    return menu_item


def get_menu(
    session: Session,
) -> list[MenuItem]:

    cached_menu = redis_client.get("menu:list")

    if cached_menu:
        return [MenuItem.model_validate(item) for item in json.loads(cached_menu)]

    menu = session.exec(
        select(MenuItem)
        .where(MenuItem.is_available == True)
        .order_by(MenuItem.name)
    ).all()

    redis_client.set(
        "menu:list",
        json.dumps([item.model_dump(mode="json") for item in menu]),
        ex=300,
    )

    return menu
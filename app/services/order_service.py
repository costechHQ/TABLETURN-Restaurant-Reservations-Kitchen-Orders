from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlmodel import Session

from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.menu_item import MenuItem
from app.models.restaurant_table import RestaurantTable
from app.schemas.order import OrderCreate, OrderItemCreate


def create_order(
    session: Session,
    data: OrderCreate,
    waiter_id: int,
) -> Order:

    # Check table exists
    table = session.get(RestaurantTable, data.table_id)

    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table not found",
        )

    order = Order(
        table_id=data.table_id,
        wait_id=waiter_id,
        status=OrderStatus.PLACED,
        create_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    session.add(order)
    session.commit()
    session.refresh(order)

    return order


def add_order_item(
    session: Session,
    order_id: int,
    data: OrderItemCreate,
) -> OrderItem:

    # Find order
    order = session.get(Order, order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    # Find menu item
    menu_item = session.get(MenuItem, data.menu_item_id)

    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    # Check availability
    if not menu_item.is_available:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Menu item is not available",
        )

    # Save current menu price on the order item
    order_item = OrderItem(
        order_id=order_id,
        menu_item_id=data.menu_item_id,
        qty=data.qty,
        unit_price=menu_item.price,
        notes=data.notes,
    )

    session.add(order_item)

    # Update order timestamp
    order.updated_at = datetime.now(timezone.utc)

    session.add(order)
    session.commit()
    session.refresh(order_item)

    return order_item
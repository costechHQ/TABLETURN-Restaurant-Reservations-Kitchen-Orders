from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.menu_item import MenuItem
from app.models.table import RestaurantTable
from app.schemas.orders import OrderCreate, OrderItemCreate
from app.services.kitchen_service import sync_order_to_kds


def create_order(
    session: Session,
    data: OrderCreate,
    waiter_id: int,
) -> Order:

    table = session.get(RestaurantTable, data.table_id)

    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table not found",
        )

    order = Order(
        table_id=data.table_id,
        waiter_id=waiter_id,
        status=OrderStatus.PLACED,
        created_at=datetime.now(timezone.utc),
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

    
    order = session.get(Order, order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    menu_item = session.get(MenuItem, data.menu_item_id)

    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    
    if not menu_item.is_available:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Menu item is not available",
        )

    # Save current menu price on the order item
    order_item = OrderItem(
    order_id=order.id,
    menu_item_id=data.menu_item_id,
    qty=data.qty,
    unit_price=menu_item.price,
    total_amount=data.qty * menu_item.price,
    notes=data.notes,
)

    session.add(order_item)
    order.total_amount += menu_item.price * data.qty
    order.updated_at = datetime.now(timezone.utc)

    session.add(order)
    session.commit()
    session.refresh(order_item)

    sync_order_to_kds(order)

    return order_item

def get_orders(
    session: Session,
    status: OrderStatus | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Order]:
    statement = select(Order)

    if status is not None:
        statement = statement.where(Order.status == status)

    statement = (
        statement
        .offset(offset)
        .limit(limit)
    )

    return session.exec(statement).all()
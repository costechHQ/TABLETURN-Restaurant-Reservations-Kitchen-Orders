from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlmodel import Session

from app.models.order import Order, OrderStatus
from app.schemas.order import OrderStatusUpdate


VALID_TRANSITIONS = {
    OrderStatus.PLACED: OrderStatus.PREPARING,
    OrderStatus.PREPARING: OrderStatus.READY,
    OrderStatus.READY: OrderStatus.SERVED,
}


def update_order_status(
    session: Session,
    order_id: int,
    data: OrderStatusUpdate,
) -> Order:

    order = session.get(Order, order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    current_status = order.status
    new_status = data.status

    expected_next_status = VALID_TRANSITIONS.get(current_status)

    if expected_next_status != new_status:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Invalid status transition: "
                f"{current_status.value} → {new_status.value}"
            ),
        )

    order.status = new_status
    order.updated_at = datetime.now(timezone.utc)

    session.add(order)
    session.commit()
    session.refresh(order)

    return order
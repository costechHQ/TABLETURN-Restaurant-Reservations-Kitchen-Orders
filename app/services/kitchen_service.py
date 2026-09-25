import json
import queue
import firebase_admin
from firebase_admin import firestore

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.order import Order, OrderStatus
from app.schemas.orders import OrderStatusUpdate
from app.core.firebase import db


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

    sync_order_to_kds(order)

    return order


def get_kitchen_queue(session: Session) -> list[Order]:
    statement = select(Order).where(
        Order.status.in_(
            [OrderStatus.PLACED, OrderStatus.PREPARING]
        )
    )

    return session.exec(statement).all()

def sync_order_to_kds(order: Order) -> None:
    items = [
        {
            "id": item.id,
            "menu_item_id": item.menu_item_id,
            "qty": item.qty,
            "unit_price": str(item.unit_price),
            "notes": item.notes,
            "status": item.status.value,
        }
        for item in order.ordered_items
    ]

    db.collection("kitchen_queue").document(str(order.id)).set({
        "order_id": order.id,
        "table_id": order.table_id,
        "waiter_id": order.waiter_id,
        "status": order.status.value,
        "total_amount": str(order.total_amount),
        "items": items,
        "updated_at": order.updated_at.isoformat(),
    })
    
def stream_kitchen_events():
    events = queue.Queue()

    query = db.collection("kitchen_queue")

    def on_snapshot(col_snapshot, changes, read_time):
        for change in changes:
            events.put({
                "type": change.type.name,
                "data": change.document.to_dict(),
            })

    watch = query.on_snapshot(on_snapshot)

    return events, watch
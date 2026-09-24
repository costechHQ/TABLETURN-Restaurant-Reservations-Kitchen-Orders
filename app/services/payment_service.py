from fastapi import HTTPException, status
from sqlmodel import Session

from app.models.order import Order
from app.models.payment import Payment, PaymentStatus
from app.schemas.payment import PaymentCreate


def create_payment(
    session: Session,
    order_id: int,
    data: PaymentCreate,
) -> Payment:
    order = session.get(Order, order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    payment = Payment(
        order_id=order.id,
        amount=order.total_amount,
        method=data.method,
        status=PaymentStatus.PENDING,
    )

    session.add(payment)
    session.commit()
    session.refresh(payment)

    return payment
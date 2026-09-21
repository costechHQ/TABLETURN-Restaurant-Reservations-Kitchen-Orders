from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.order import Order
from app.models.payment import Payment, PaymentStatus
from app.schemas.payment import PaymentCreate


def record_payment(
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

    existing_payment = session.exec(
        select(Payment).where(
            Payment.order_id == order_id,
            Payment.status == PaymentStatus.SUCCESS,
        )
    ).first()

    if existing_payment:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Order has already been paid",
        )

    payment = Payment(
        order_id=order_id,
        amount=data.amount,
        method=data.method,
        status=PaymentStatus.SUCCESS,
        recorded_at=datetime.now(timezone.utc),
    )

    session.add(payment)
    session.commit()
    session.refresh(payment)

    return payment
from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.order import Order, OrderStatus
from app.models.processed_event import ProcessedEvent
from app.models.payment import Payment, PaymentStatus



def process_payment_webhook(
    session: Session,
    event_id: str,
    reference: str,
    payment_status: str,
) -> None:
    existing_event = session.exec(
        select(ProcessedEvent).where(
            ProcessedEvent.event_id == event_id
        )
    ).first()

    if existing_event:
        return

    payment = session.exec(
        select(Payment).where(
            Payment.reference == reference
        )
    ).first()

    if not payment:
        return

    if payment_status == "success":
        payment.status = PaymentStatus.SUCCESS

        order = session.get(Order, payment.order_id)

        if order:
            order.status = OrderStatus.PAID
            session.add(order)

    processed_event = ProcessedEvent(event_id=event_id)

    session.add(payment)
    session.add(processed_event)
    session.commit()
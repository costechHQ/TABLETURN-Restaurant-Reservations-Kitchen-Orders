from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.processed_event import ProcessedEvent
from app.models.payment import Payment, PaymentStatus


def process_payment_webhook(
    session: Session,
    event_id: str,
    reference: str,
    payment_status: str,
) -> None:

    # Check if this event was already processed
    existing_event = session.exec(
        select(ProcessedEvent).where(
            ProcessedEvent.event_id == event_id
        )
    ).first()

    if existing_event:
        # Duplicate webhook
        return

    # Find payment using the reference
    payment = session.exec(
        select(Payment).where(
            Payment.id == int(reference)
        )
    ).first()

    if not payment:
        # Unknown reference.
        # The brief says this should return 200 and be logged.
        return

    # Update payment
    if payment_status == "success":
        payment.status = PaymentStatus.SUCCESS

    # Record event
    processed_event = ProcessedEvent(
        event_id=event_id,
    )

    session.add(processed_event)
    session.add(payment)

    session.commit()
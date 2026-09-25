from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

from sqlmodel import Session, select

from app.models.payment import Payment, PaymentStatus


def get_daily_turnover(
    session: Session,
    report_date: date,
) -> Decimal:
    start_of_day = datetime.combine(
        report_date,
        time.min,
        tzinfo=timezone.utc,
    )

    start_of_next_day = datetime.combine(
        report_date + timedelta(days=1),
        time.min,
        tzinfo=timezone.utc,
    )

    payments = session.exec(
        select(Payment).where(
            Payment.status == PaymentStatus.SUCCESS,
            Payment.recorded_at >= start_of_day,
            Payment.recorded_at < start_of_next_day,
        )
    ).all()

    total = sum(
        (payment.amount for payment in payments),
        Decimal("0"),
    )

    return total
from datetime import date, datetime, time, timezone
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

    end_of_day = datetime.combine(
        report_date,
        time.max,
        tzinfo=timezone.utc,
    )

    payments = session.exec(
        select(Payment).where(
            Payment.status == PaymentStatus.SUCCESS,
            Payment.recorded_at >= start_of_day,
            Payment.recorded_at <= end_of_day,
        )
    ).all()

    total = sum(
        (payment.amount for payment in payments),
        Decimal("0"),
    )

    return total
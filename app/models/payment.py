from sqlmodel import SQLModel, Field
from enum import Enum
from decimal import Decimal
from datetime import datetime, timezone


class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class Payment(SQLModel, table=True):
    __tablename__ = "payments"

    id: int | None = Field(
        default=None,
        primary_key=True
    )

    order_id: int = Field(
        foreign_key="orders.id",
        index=True
    )

    amount: Decimal

    method: str

    recorded_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    status: PaymentStatus = Field(
        default=PaymentStatus.PENDING,
        index=True
    )
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

from sqlmodel import Field, SQLModel


class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class Payment(SQLModel, table=True):
    __tablename__ = "payments"

    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    order_id: int = Field(
        foreign_key="orders.id",
        index=True,
    )

    reference: str = Field(
        unique=True,
        index=True,
    )

    amount: Decimal

    method: str

    recorded_by: int = Field(
        foreign_key="users.id",
        index=True,
    )

    recorded_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    status: PaymentStatus = Field(
        default=PaymentStatus.PENDING,
        index=True,
    )
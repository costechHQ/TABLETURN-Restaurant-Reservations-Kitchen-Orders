from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime
from sqlmodel import Field, Index, SQLModel


class ReservationStatus(str, Enum):
    CONFIRMED = "confirmed"
    SEATED = "seated"
    CANCELLED = "cancelled"


class Reservation(SQLModel, table=True):
    __tablename__ = "reservations"

    id: int | None = Field(
        default=None,
        primary_key=True
    )
    table_id: int = Field(
        foreign_key="restaurant_tables.id",
        index=True
    )
    diner_id: int = Field(
        foreign_key="users.id",
        index=True,
    )
    party_size: int

    start_at: datetime = Field(
        index=True,
        sa_type=DateTime(timezone=True),
    )

    end_at: datetime = Field(
        sa_type=DateTime(timezone=True),
    )

    status: ReservationStatus = Field(
        default=ReservationStatus.CONFIRMED
    )

    __table_args__ = (
        Index(
            "ix_reservations_table_start_end",
            "table_id",
            "start_at",
            "end_at",
        ),
    )
from datetime import datetime
from enum import Enum
from sqlmodel import Field, SQLModel

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
    start_at: datetime = Field(index=True)
    end_at: datetime
    status: ReservationStatus = Field(
        default=ReservationStatus.CONFIRMED
    )
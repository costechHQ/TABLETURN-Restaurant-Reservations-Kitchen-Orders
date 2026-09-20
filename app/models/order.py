from datetime import datetime, timezone
from enum import Enum
from sqlmodel import Field, Relationship, SQLModel
from decimal import Decimal


class OrderStatus(str, Enum):
    PLACED = "placed"
    PREPARING = "preparing"
    READY = "ready"
    SERVED = "served"


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: int | None = Field(default=None, primary_key=True)

    table_id: int = Field(
        foreign_key="restaurant_tables.id",
        index=True,
    )

    wait_id: int = Field(
        foreign_key="users.id",
        index=True,
    )

    status: OrderStatus = Field(
        default=OrderStatus.PLACED,
        index=True,
    )

    total_amount: Decimal = Field(
        default=Decimal("0.00"),
    )

    create_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    ordered_items: list["OrderItem"] = Relationship(
        back_populates="order"
    )
    
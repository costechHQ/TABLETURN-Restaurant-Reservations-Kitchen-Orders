from sqlmodel import Field, Relationship, SQLModel
from decimal import Decimal
from enum import Enum

class OrderItemStatus(str, Enum):
    PENDING = "pending"
    PREPARING = "preparing"
    READY = "ready"
    SERVED = "served"

class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"

    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    order_id: int = Field(
        foreign_key="orders.id",
        index=True
    )

    menu_item_id: int = Field(
        foreign_key="menu_items.id",
        index=True
    )

    qty: int

    unit_price: Decimal

    total_amount: Decimal

    notes: str | None = Field(
        default=None,
        max_length=200,
    )

    status: OrderItemStatus = Field(
        default=OrderItemStatus.PENDING,
        index=True
    )

    order: "Order" = Relationship(
        back_populates="ordered_items"
    )

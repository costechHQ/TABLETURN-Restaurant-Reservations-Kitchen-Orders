from datetime import datetime
from pydantic import BaseModel, Field, computed_field
from app.models.order import OrderStatus
from app.models.order_item import OrderItemStatus
from decimal import Decimal

class OrderCreate(BaseModel):
    table_id: int = Field(gt=0)


class OrderItemCreate(BaseModel):
    menu_item_id: int
    qty: int = Field(gt=0)
    notes: str | None = Field(default=None, max_length=200)


class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    menu_item_id: int
    qty: int
    unit_price: Decimal
    total_amount: Decimal
    notes: str | None
    status: OrderItemStatus

    @computed_field
    @property
    def total_price(self) -> Decimal:
        return self.qty * self.unit_price


class OrderResponse(BaseModel):
    id: int
    table_id: int
    waiter_id: int
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    ordered_items: list[OrderItemResponse]


class OrderStatusUpdate(BaseModel):
    status: OrderStatus

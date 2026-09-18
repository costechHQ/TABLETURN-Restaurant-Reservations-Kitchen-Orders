from datetime import datetime
from pydantic import BaseModel, Field
from app.models.order import OrderStatus
from app.models.order_item import OrderItemStatus

class orderCreate(BaseModel):
    table_id: int


class orderItemCreate(BaseModel):
    menu_item_id: int
    qty: int = Field(gt=0)
    notes: str | None = Field(default=None, max_length=200)


class orderItemResponse(BaseModel):
    id: int
    order_id: int
    menu_item_id: int
    qty: int
    unit_price: float
    notes: str | None
    status: OrderItemStatus


class OrderResponse(BaseModel):
    id: int
    table_id: int
    waiter_id: int
    status: OrderStatus
    created_at: datetime
    updated_at: datetime


class OrderStatusUpdate(BaseModel):
    status: OrderStatus

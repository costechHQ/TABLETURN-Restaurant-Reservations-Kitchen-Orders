from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.payment import PaymentStatus


class PaymentCreate(BaseModel):
    method: str


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    amount: Decimal
    method: str
    recorded_at: datetime
    status: PaymentStatus

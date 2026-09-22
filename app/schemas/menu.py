from decimal import Decimal
from pydantic import BaseModel, Field


class MenuItemCreate(BaseModel):
    name: str
    description: str = Field(default=None, min_length=20, max_length=150)
    price: Decimal = Field(gt=0)
    is_available: bool | None = None


class MenuItemResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: Decimal
    is_available: bool

class MenuItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = Field(default=None, min_length=20, max_length=150)
    price: Decimal | None = Field(default=None, gt=0)
    is_available: bool | None = None
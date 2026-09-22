from decimal import Decimal
from sqlmodel import Field, SQLModel

class MenuItem(SQLModel, table=True):
    __tablename__ = "menu_items"
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str | None = Field(default=None, min_length=20, max_length=150)
    price: Decimal
    is_available: bool = True

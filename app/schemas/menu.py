from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class MenuItemCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Jollof Rice with Grilled Chicken",
                "description": "Fragrant Nigerian-style jollof rice served with grilled chicken and fried plantain.",
                "price": 4500,
                "is_available": True
            }
        }
    )

    name: str = Field(
        min_length=2,
        max_length=100,
        examples=["Jollof Rice with Grilled Chicken"]
    )

    description: str | None = Field(
        default=None,
        min_length=20,
        max_length=150,
        examples=[
            "Fragrant Nigerian-style jollof rice served with grilled chicken and fried plantain."
        ]
    )

    price: Decimal = Field(
        gt=0,
        examples=[4500]
    )

    is_available: bool = Field(
        default=True,
        examples=[True]
    )


class MenuItemResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: Decimal
    is_available: bool


class MenuItemUpdate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Jollof Rice with Grilled Chicken",
                "description": "Fragrant Nigerian-style jollof rice served with grilled chicken and fried plantain.",
                "price": 4500,
                "is_available": True
            }
        }
    )

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
        examples=["Jollof Rice with Grilled Chicken"]
    )

    description: str | None = Field(
        default=None,
        min_length=20,
        max_length=150,
        examples=[
            "Fragrant Nigerian-style jollof rice served with grilled chicken and fried plantain."
        ]
    )

    price: Decimal | None = Field(
        default=None,
        gt=0,
        examples=[4500]
    )

    is_available: bool | None = Field(
        default=None,
        examples=[True]
    )
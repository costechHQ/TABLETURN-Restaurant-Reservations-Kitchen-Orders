from sqlmodel import Field, SQLModel

class RestaurantTable(SQLModel, table=True):
    __tablename__ = "restaurant_tables"

    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(unique=True, index=True)
    capacity: int
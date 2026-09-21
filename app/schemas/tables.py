from pydantic import BaseModel, Field

class TableCreate(BaseModel):
    code: str = "TO1"
    capacity: int = Field(gt=0)


class TableResponse(BaseModel):
    id: int
    code: str
    capacity: int

class TableUpdate(BaseModel):
    code: str | None = None
    capacity: int | None = Field(default=None, gt=0)
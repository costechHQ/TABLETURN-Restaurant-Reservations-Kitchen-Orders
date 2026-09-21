from pydantic import BaseModel, Field

class TableCreate(BaseModel):
    code: str
    capacity: int = Field(gt=0)


class TableResponse(BaseModel):
    id: int
    code: str
    capacity: int





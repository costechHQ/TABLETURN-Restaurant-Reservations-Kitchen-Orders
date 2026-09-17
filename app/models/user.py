from pydantic import BaseModel
import uuid

my_uuid = uuid.uuid4


class Users(BaseModel):
    id: uuid
    email: str
    password_hash: str
    role: str
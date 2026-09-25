from datetime import datetime, timezone
from enum import Enum

from sqlmodel import Field, SQLModel


class UserRole(str, Enum):
    DINER = "diner"
    WAITER = "waiter"
    KITCHEN = "kitchen"
    MANAGER = "manager"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    email: str = Field(
        unique=True,
        index=True,
    )

    password_hash: str

    role: UserRole = Field(
        default=UserRole.DINER,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
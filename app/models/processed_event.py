from datetime import datetime, timezone
from sqlmodel import Field, SQLModel



class ProcessedEvent(SQLModel, table=True):
    __tablename__ = "processed_events"

    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    event_id: str = Field(
        unique=True,
        index=True,
    )

    processed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
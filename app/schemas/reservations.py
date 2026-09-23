from datetime import datetime

from pydantic import BaseModel, Field
from app.models.reservation import ReservationStatus

class ReservationCreate(BaseModel):
    table_id: int = 1
    party_size: int = Field(default=2, gt=0)
    start_at: datetime = "2026-09-22T15:00:00"
    end_at: datetime = "2026-09-22T16:00:00"


class ReservationResponse(BaseModel):
    id: int
    table_id: int
    diner_id: int
    party_size: int
    start_at: datetime
    end_at: datetime
    status: ReservationStatus


class ReservationActionResponse(BaseModel):
    id: int
    status: ReservationStatus


class AvailabilityQuery(BaseModel):
    party_size: int = Field(gt=0)
    start_at: datetime
    end_at: datetime

class ReservationUpdate(BaseModel):
    table_id: int
    party_size: int = Field(gt=0)
    start_at: datetime
    end_at: datetime
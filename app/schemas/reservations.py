from datetime import datetime

from pydantic import BaseModel, Field
from app.models.reservation import ReservationStatus

class ReservationCreate(BaseModel):
    table_id: int 
    party_size: int = Field(gt=0)
    start_at: datetime
    end_at: datetime


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
    # table_id: int
    party_size: int = Field(gt=0)
    start_at: datetime
    end_at: datetime
    # is_available: bool
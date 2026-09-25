from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class TurnoverResponse(BaseModel):
    date: date
    total: Decimal
from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select
from fastapi import HTTPException

from datetime import datetime
from app.schemas.reservations import AvailabilityQuery
from app.services.reservation_service import check_availability

from app.core.deps import get_current_user, require_role
from app.db.session import get_session
from app.models.user import User, UserRole
from app.schemas.tables import TableCreate, TableUpdate
from app.models.table import RestaurantTable


router = APIRouter(
    prefix="/tables",
    tags=["Tables"],
)

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)

def create_table(
    data: TableCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[
        User,
        Depends(require_role(UserRole.MANAGER.value)),
    ],
):

    table = RestaurantTable(
        code=data.code,
        capacity=data.capacity,
    )

    session.add(table)
    session.commit()
    session.refresh(table)

    return table



@router.get("/availability")
def get_table_availability(
    party_size: int,
    start: datetime,
    end: datetime,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[
        User,
        Depends(require_role(UserRole.DINER.value)),
    ],
):
    data = AvailabilityQuery(
        party_size=party_size,
        start=start,
        end=end,
    )

    return check_availability(
        session=session,
        data=data,
    )
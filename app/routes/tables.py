from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.core.deps import require_role
from app.db.session import get_session
from app.models.user import User, UserRole
from app.schemas.tables import TableCreate
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



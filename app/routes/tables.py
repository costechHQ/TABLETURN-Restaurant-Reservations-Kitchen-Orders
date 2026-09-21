from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select
from fastapi import HTTPException

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


@router.get("")
def get_tables(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return session.exec(select(RestaurantTable)).all()


@router.get("/{table_id}")
def get_table(
    table_id: int,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    table = session.get(RestaurantTable, table_id)

    if table is None:
        raise HTTPException(
            status_code=404,
            detail="Table not found",
        )

    return table


@router.put("/{table_id}")
def update_table(
    table_id: int,
    data: TableUpdate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[
        User,
        Depends(require_role(UserRole.MANAGER.value)),
    ],
):
    table = session.get(RestaurantTable, table_id)

    if table is None:
        raise HTTPException(
            status_code=404,
            detail="Table not found",
        )

    if data.code is not None:
        table.code = data.code

    if data.capacity is not None:
        table.capacity = data.capacity

    session.add(table)
    session.commit()
    session.refresh(table)

    return table


@router.delete("/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_table(
    table_id: int,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[
        User,
        Depends(require_role(UserRole.MANAGER.value)),
    ],
):
    table = session.get(RestaurantTable, table_id)

    if table is None:
        raise HTTPException(
            status_code=404,
            detail="Table not found",
        )

    session.delete(table)
    session.commit()
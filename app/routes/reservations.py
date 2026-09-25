from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.deps import get_current_user
from app.db.session import get_session
from app.models.user import User, UserRole
from app.schemas.reservations import ReservationCreate, ReservationResponse
from app.services.reservation_service import (
    cancel_reservation as cancel_reservation_service,
    create_reservation as create_reservation_service,
)


router = APIRouter(
    prefix="/reservations",
    tags=["Reservations"],
)


@router.post(
    "",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_reservation(
    data: ReservationCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.role != UserRole.DINER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only diners can create reservations",
        )

    return create_reservation_service(
        session=session,
        data=data,
        diner_id=current_user.id,
    )


@router.post(
    "/{reservation_id}/cancel",
    response_model=ReservationResponse,
    status_code=status.HTTP_200_OK,
)
def cancel_reservation(
    reservation_id: int,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.role not in (UserRole.DINER, UserRole.WAITER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the reservation owner or a waiter can cancel reservations",
        )

    return cancel_reservation_service(
        session=session,
        reservation_id=reservation_id,
        user=current_user,
    )
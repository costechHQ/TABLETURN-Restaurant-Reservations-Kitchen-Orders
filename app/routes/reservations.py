from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.services.reservation_service import (
    create_reservation as create_reservation_service,
    get_reservations,
    check_availability,
)

from app.core.deps import get_current_user
from app.db.session import get_session
from app.models.user import User, UserRole
from app.schemas.reservations import (
    AvailabilityQuery,
    ReservationCreate, 
    ReservationResponse,
)

from app.models.table import RestaurantTable



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
            detail="Only diners can create reservations"
        )

    # if data.start_at >= data.end_at:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="End time must be after start time",
    #     )

    # table = session.get(RestaurantTable, data.table_id)

    # if table is None:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="Table not found"
    #     )

    # if data.party_size > table.capacity:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Party size exceeds table capacity",
    #     )

    # overlapping_reservation = session.exec(
    #     select(Reservation).where(
    #         Reservation.table_id == data.table_id,
    #         Reservation.status != "cancelled",
    #         Reservation.start_at < data.end_at,
    #         Reservation.end_at > data.start_at,
    #     )
    # ).first()

    # if overlapping_reservation:
    #     raise HTTPException(
    #         status_code=status.HTTP_409_CONFLICT,
    #         detail="Table is already reserved for this time",
    #     )

    # reservation = Reservation(
    #     table_id=data.table_id,
    #     diner_id=current_user.id,
    #     party_size=data.party_size,
    #     start_at=data.start_at,
    #     end_at=data.end_at,
    # )

    # session.add(reservation)
    # session.commit()
    # session.refresh(reservation)

    return create_reservation_service(
        session=session,
        data=data,
        diner_id=current_user.id,
    )

@router.get(
    "",
    response_model=list[ReservationResponse],
)

def get_all_reservations(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):

    
    return get_reservations(
        session=session,
        user=current_user,
    )

@router.get(
    "/availabilty",
    response_model=list[RestaurantTable],
)
def check_reservation_availability(
    data: Annotated[AvailabilityQuery, Depends()],
    session: Annotated[Session, Depends(get_session)],
):

    return check_availability(
        session=session,
        data=data,
    )
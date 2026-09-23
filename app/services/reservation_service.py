from datetime import datetime

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.reservation import (
    Reservation,
    ReservationStatus,
)
from app.models.table import RestaurantTable
from app.schemas.reservations import ReservationCreate
from app.models.user import User, UserRole


def create_reservation(
    session: Session,
    data: ReservationCreate,
    diner_id: int,
) -> Reservation:


    # Check that the end time is after the start time
    if data.end_at <= data.start_at:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="End time must be after start time",
        )

    # Check that reservation does not start in the past
    if data.start_at < datetime.now(data.start_at.tzinfo):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Reservation cannot start in the past",
        )

    # Find the table
    table = session.get(RestaurantTable, data.table_id)

    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table not found",
        )

    # Check table capacity
    if data.party_size > table.capacity:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Party size exceeds table capacity",
        )

    # Lock reservations for this table
    existing_reservations = session.exec(
        select(Reservation)
        .where(
            Reservation.table_id == data.table_id,
            Reservation.status != ReservationStatus.CANCELLED,
        )
        .with_for_update()
    ).all()

    # Exact overlap check
    for reservation in existing_reservations:

        overlaps = (
            data.start_at < reservation.end_at
            and data.end_at > reservation.start_at
        )

        if overlaps:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Table is already reserved during this time",
            )

    # Create reservation
    reservation = Reservation(
        table_id=data.table_id,
        diner_id=diner_id,
        party_size=data.party_size,
        start_at=data.start_at,
        end_at=data.end_at,
        status=ReservationStatus.CONFIRMED,
    )

    session.add(reservation)
    session.commit()
    session.refresh(reservation)

    return reservation


def get_reservations(
            session: Session,
            user: User,
    ) -> list[Reservation]:

    if user.role == UserRole.DINER:
        return session.exec(
            select(Reservation).where(
                Reservation.diner_id == user.id
            )
        ).all()

    if user.role in (UserRole.WAITER, UserRole.MANAGER):
        return session.exec(
            select(Reservation)
        ).all()

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have access to reservations",
    )
from datetime import datetime

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.reservation import (
    Reservation,
    ReservationStatus,
)
from app.models.table import RestaurantTable
from app.schemas.reservations import (
    AvailabilityQuery,
    ReservationCreate,
    ReservationUpdate
)
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



def check_availability(
        session: Session,
        data: AvailabilityQuery,
) -> list[RestaurantTable]:

    if data.end <= data.start:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="End time must be after start time",
    )

    tables = session.exec(
        select(RestaurantTable).where(
            RestaurantTable.capacity >= data.party_size
        )
    ).all()

    available_tables = []

    for table in tables:
        reservations = session.exec(
            select(Reservation).where(
                Reservation.table_id == table.id,
                Reservation.status != ReservationStatus.CANCELLED,
            )
        ).all()

        has_overlap = any(
            data.start < reservation.end_at
            and data.end > reservation.start_at
            for reservation in reservations
        )

        if not has_overlap:
            available_tables.append(table)

    return available_tables


def update_reservation(
        session: Session,
        reservation_id: int,
        data: ReservationUpdate,
        user: User,
) -> Reservation:
    reservation = session.get(Reservation, reservation_id)

    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found",
        )

    if user.role == UserRole.DINER and reservation.diner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own reservations",
        )

    if user.role not in (UserRole.DINER, UserRole.MANAGER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update reservations",
        )

    if reservation.status == ReservationStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cancelled reservations cannot be updated",
        )

    if data.end_at <= data.start_at:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="End time must be after start time",
        )

    if data.start_at < datetime.now(data.start_at.tzinfo):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Reservation cannot start in the past",
        )

    table = session.get(RestaurantTable, data.table_id)

    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table not found",
        )

    if data.party_size > table.capacity:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Party size exceeds table capacity",
        )

    existing_reservations = session.exec(
        select(Reservation).where(
            Reservation.table_id == data.table_id,
            Reservation.id != reservation.id,
            Reservation.status != ReservationStatus.CANCELLED,
        )
    ).all()

    for existing in existing_reservations:
        overlaps = (
            data.start_at < existing.end_at
            and data.end_at > existing.start_at
        )

        if overlaps:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Table is already reserved during this time",
            )

    reservation.table_id = data.table_id
    reservation.party_size = data.party_size
    reservation.start_at = data.start_at
    reservation.end_at = data.end_at

    session.add(reservation)
    session.commit()
    session.refresh(reservation)

    return reservation


def cancel_reservation(
        session: Session,
        reservation_id: int,
        user: User,
) -> Reservation:

    reservation = session.get(Reservation, reservation_id)

    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found"
        )

    if user.role == UserRole.DINER and reservation.diner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only cancel your own reservations",
        )

    if user.role not in (UserRole.DINER, UserRole.MANAGER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to cancel reservations",
        )

    if reservation.status == ReservationStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Reservation is already cancelled",
        )

    reservation.status = ReservationStatus.CANCELLED

    session.add(reservation)
    session.commit()
    session.refresh(reservation)

    return reservation
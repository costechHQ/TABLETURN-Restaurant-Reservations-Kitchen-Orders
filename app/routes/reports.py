from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.deps import get_current_user
from app.db.session import get_session
from app.models.user import User, UserRole
from app.schemas.reports import TurnoverResponse
from app.services.report_service import get_daily_turnover


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


@router.get(
    "/turnover",
    response_model=TurnoverResponse,
    status_code=status.HTTP_200_OK,
)
def get_turnover(
    date: date,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can view turnover reports",
        )

    total = get_daily_turnover(
        session=session,
        report_date=date,
    )

    return TurnoverResponse(
        date=date,
        total=total,
    )
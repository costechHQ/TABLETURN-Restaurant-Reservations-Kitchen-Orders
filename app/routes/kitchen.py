from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.database import get_session
from app.models.user import User, UserRole
from app.core.deps import require_role
from app.services.kitchen_service import get_kitchen_queue

router = APIRouter(
    prefix="/kitchen"
    tags=["/kitchen"]
)


@router.get("/queue")
def kitchen_queue(
    session: Sesssion = Depends(get_session),
    current_user: User = Depends(
        require_role(UserRole.KITCHEN)
    ),
):
    return get_kitchen_queue(session)
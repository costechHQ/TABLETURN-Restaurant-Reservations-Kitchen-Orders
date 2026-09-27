from fastapi import APIRouter, Depends, Request, status
from sqlmodel import Session

from app.core.rate_limit import limiter
from app.core.deps import require_role
from app.models.user import User, UserRole

from app.services.auth_service import (
    register_user, 
    login_user,
    create_staff_user,
)

from app.db.session import get_session

from app.schemas.auth import (
    RegisterRequest,
    UserResponse,
    TokenResponse,
    LoginRequest,
    StaffCreateRequest,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)

def register(
    data: RegisterRequest,
    session: Session = Depends(get_session),
):
    return register_user(session, data)


@router.post(
    "/staff",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_staff(
    data: StaffCreateRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(
        require_role(UserRole.MANAGER)
    ),
):
    return create_staff_user(session, data)


@router.post(
    "/login",
    response_model=TokenResponse,
)
@limiter.limit("5/minute")
def login(
    request: Request,
    data: LoginRequest,
    session: Session = Depends(get_session),
):
    access_token = login_user(session, data)

    return TokenResponse(
        access_token=access_token,
    )
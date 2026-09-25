from fastapi import APIRouter, Depends, Request, status
from sqlmodel import Session

from app.core.rate_limit import limiter

from app.services.auth_service import register_user, login_user
from app.db.session import get_session
from app.schemas.auth import (
    RegisterRequest,
    UserResponse,
    TokenResponse,
    LoginRequest,
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
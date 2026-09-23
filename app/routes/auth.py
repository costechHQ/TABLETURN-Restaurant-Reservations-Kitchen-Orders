from fastapi import APIRouter, Depends, status
from sqlmodel import Session

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
    # existing_user = session.exec(
    #     select(User).where(User.email == data.email)
    # ).first()

    # if existing_user:
    #     raise HTTPException(
    #         status_code=status.HTTP_409_CONFLICT,
    #         detail="Email already registered",
    #     )

    # user = User(
    #     email=data.email,
    #     password_hash=hash_password(data.password),
    #     role=data.role,
    # )

    # session.add(user)
    # session.commit()
    # session.refresh(user)

    # return user

    return register_user(session, data)


@router.post(
    "/login",
    response_model=TokenResponse,
)

def login(
    data: LoginRequest,
    session: Session = Depends(get_session),
):
    # user = session.exec(
    #     select(User).where(User.email == data.email)
    # ).first()

    # if user is None or not verify_password(data.password, user.password_hash):
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid email or password",
    #     )

    # access_token = create_access_token(
    #     user_id=user.id,
    #     role=user.role.value,
    # )

    access_token = login_user(session, data)
    return TokenResponse(access_token=access_token)
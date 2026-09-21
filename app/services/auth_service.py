from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
)


def register_user(
    session: Session,
    data: RegisterRequest,
) -> User:
    # Check if email already exists
    existing_user = session.exec(
        select(User).where(User.email == data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Hash the password before saving
    hashed_password = get_password_hash(data.password)

    user = User(
        email=data.email,
        password_hash=hashed_password,
        role=data.role,
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


def login_user(
    session: Session,
    data: LoginRequest,
) -> str:
    # Find user
    user = session.exec(
        select(User).where(User.email == data.email)
    ).first()

    # User does not exist
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Check password
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Create JWT
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role.value,
        }
    )

    return access_token
from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)

def register_user(
    session: Session,
    data: RegisterRequest,
) -> User:
    
    existing_user = session.exec(
        select(User).where(User.email == data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    hashed_password = hash_password(data.password)

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
    
    user = session.exec(
        select(User).where(User.email == data.email)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        user_id=user.id,
        role=user.role.value,
    )

    return access_token
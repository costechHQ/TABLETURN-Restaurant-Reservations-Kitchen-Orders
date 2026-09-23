from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from app.db.session import get_session
from app.schemas.menu import MenuItemCreate, MenuItemResponse, MenuItemUpdate
from app.services.menu_service import create_menu_item, get_menu, update_menu_item
from app.core.deps import get_current_user, require_role
from app.models.user import User, UserRole

router = APIRouter(
    prefix="/menu",
    tags=["Menu"],
)

@router.post(
    "",
    response_model=MenuItemResponse,
    status_code=status.HTTP_201_CREATED,
)

def create_menu(
    data: MenuItemCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[
        User, 
        Depends(require_role(UserRole.MANAGER.value)),
    ]
):

    return create_menu_item(
        session=session,
        data=data,
    )

@router.get(
    "",
    response_model=list[MenuItemResponse],
)

def get_menu_items(
    session: Annotated[Session, Depends(get_session)],
):
    return get_menu(session)

@router.put(
    "/{menu_item_id}",
    response_model=MenuItemResponse,
)

def update_menu(
    menu_item_id: int,
    data: MenuItemUpdate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[
        User,
        Depends(require_role(UserRole.MANAGER.value))
    ]
):
    return update_menu_item(
        session=session,
        menu_item_id=menu_item_id,
        data=data,
    )
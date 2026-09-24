from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.db.session import get_session
from app.models.user import User, UserRole
from app.schemas.orders import (
    OrderCreate,
    OrderResponse,
    OrderItemCreate,
    OrderItemResponse,
    OrderStatusUpdate,
)
from app.services.order_service import (
    create_order,
    add_order_item,
)
from app.services.kitchen_service import update_order_status
from app.core.deps import get_current_user, require_role

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_order(
    data: OrderCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(
        require_role(UserRole.WAITER)
    ),
):
    return create_order(
        session=session,
        data=data,
        waiter_id=current_user.id,
    )


@router.post(
    "/{order_id}/items",
    response_model=OrderItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_item_to_order(
    order_id: int,
    data: OrderItemCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(
        require_role(UserRole.WAITER)
    ),
):
    return add_order_item(
        session=session,
        order_id=order_id,
        data=data,
    )


@router.post(
    "/{order_id}/status",
    response_model=OrderResponse,
)
def change_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(
        require_role(
            UserRole.KITCHEN,
            UserRole.WAITER,
        )
    ),
):
    return update_order_status(
        session=session,
        order_id=order_id,
        data=data,
    )
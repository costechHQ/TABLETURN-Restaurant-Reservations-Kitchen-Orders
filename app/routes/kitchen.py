import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from app.core.deps import require_role
from app.db.session import get_session
from app.models.user import User, UserRole
from app.schemas.orders import KitchenQueueResponse
from app.services.kitchen_service import (
    get_kitchen_queue,
    stream_kitchen_events,
)


router = APIRouter(prefix="/kitchen", tags=["kitchen"])


@router.get("/queue", response_model=list[KitchenQueueResponse])
def kitchen_queue(
    session: Session = Depends(get_session),
    current_user: User = Depends(
        require_role(UserRole.KITCHEN)
    ),
):
    return get_kitchen_queue(session)


def event_generator():
    events, watch = stream_kitchen_events()

    try:
        yield "data: connected\n\n"

        while True:
            event = events.get()

            print("SSE EVENT:", event)

            yield f"data: {json.dumps(event)}\n\n"

    finally:
        watch.unsubscribe()


@router.get("/stream")
def kitchen_stream(
    current_user: User = Depends(
        require_role(
            UserRole.KITCHEN,
            UserRole.WAITER,
        )
    ),
):
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
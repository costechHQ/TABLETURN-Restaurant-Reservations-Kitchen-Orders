import hashlib
import hmac

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Header,
    HTTPException,
    Request,
    status,
)
from sqlmodel import Session

from app.core.config import settings
from app.db.session import get_session
from app.services.background_service import log_webhook_processed
from app.services.webhook_service import process_payment_webhook


router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"],
)


@router.post("/payment")
async def payment_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_paystack_signature: str | None = Header(default=None),
    session: Session = Depends(get_session),
):
    if not x_paystack_signature:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Paystack signature",
        )

    body = await request.body()

    expected_signature = hmac.new(
        settings.secret_key.encode(),
        body,
        hashlib.sha512,
    ).hexdigest()

    if not hmac.compare_digest(
        expected_signature,
        x_paystack_signature,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Paystack signature",
        )

    payload = await request.json()

    event_id = payload["data"]["id"]
    reference = payload["data"]["reference"]
    payment_status = payload["data"]["status"]

    process_payment_webhook(
        session=session,
        event_id=event_id,
        reference=reference,
        payment_status=payment_status,
    )

    background_tasks.add_task(
        log_webhook_processed,
        event_id,
        reference,
    )

    return {"message": "Webhook processed"}
from pydantic import BaseModel

class PaymentWebhook(BaseModel):
    event_id: str
    reference: str
    status: str
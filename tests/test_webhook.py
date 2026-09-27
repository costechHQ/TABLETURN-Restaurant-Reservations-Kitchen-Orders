import hashlib
import hmac
import json
from decimal import Decimal

from sqlmodel import Session

from app.core.config import settings
from app.core.security import hash_password
from app.db.database import engine
from app.models.order import Order, OrderStatus
from app.models.payment import Payment, PaymentStatus
from app.models.table import RestaurantTable
from app.models.user import User, UserRole


def test_valid_payment_webhook_marks_payment_success_and_order_paid(client):
    with Session(engine) as session:
        table = RestaurantTable(
            code="T07",
            capacity=4,
        )

        waiter = User(
            email="pytest_webhook@example.com",
            password_hash=hash_password("TestPassword123!"),
            role=UserRole.WAITER,
        )

        session.add(table)
        session.add(waiter)
        session.commit()

        session.refresh(table)
        session.refresh(waiter)

        order = Order(
            table_id=table.id,
            waiter_id=waiter.id,
            status=OrderStatus.PLACED,
            total_amount=Decimal("3000.00"),
        )

        session.add(order)
        session.commit()
        session.refresh(order)

        payment = Payment(
        order_id=order.id,
        reference="WEBHOOK-TEST-001",
        amount=Decimal("3000.00"),
        method="online",
        recorded_by=waiter.id,
        status=PaymentStatus.PENDING,
    )

        session.add(payment)
        session.commit()

        order_id = order.id
        payment_id = payment.id

    payload = {
        "data": {
            "id": "event-001",
            "reference": "WEBHOOK-TEST-001",
            "status": "success",
        }
    }

    body = json.dumps(payload).encode()

    signature = hmac.new(
        settings.paystack_secret_key.encode(),
        body,
        hashlib.sha512,
    ).hexdigest()

    response = client.post(
        "/api/v1/webhooks/payment",
        content=body,
        headers={
            "x-paystack-signature": signature,
            "content-type": "application/json",
        },
    )

    assert response.status_code == 200

    with Session(engine) as session:
        payment = session.get(Payment, payment_id)
        order = session.get(Order, order_id)

        assert payment.status == PaymentStatus.SUCCESS
        assert order.status == OrderStatus.PAID

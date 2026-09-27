from datetime import datetime, timezone

from app.core.firebase import db


def add_floor_feed_event(
    event_type: str,
    *,
    reservation_id: int | None = None,
    order_id: int | None = None,
    table_id: int | None = None,
) -> None:
    event = {
        "type": event_type,
        "reservation_id": reservation_id,
        "order_id": order_id,
        "table_id": table_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    db.collection("floor_feed").add(event)

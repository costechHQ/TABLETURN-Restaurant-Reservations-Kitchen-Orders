import json

from datetime import datetime

from pathlib import Path

from sqlmodel import Session, select

from app.db.session import engine

from app.models.reservation import Reservation
from app.models.table import RestaurantTable


RESERVATIONS_FILE = (
    Path(__file__).resolve().parents[2]
    / "app"
    / "data"
    / "reservations.json"
)


def seed_reservations():
    with open(RESERVATIONS_FILE, "r", encoding="utf-8") as file:
        reservations = json.load(file)

    with Session(engine) as session:
        added = 0
        skipped = 0

        for item in reservations:
            # Prevent duplicate reservations
            existing_reservation = session.exec(
                select(Reservation).where(
                    Reservation.id == item["id"]
                )
            ).first()

            if existing_reservation:
                skipped += 1
                continue

            # Find the restaurant table using its code
            table = session.exec(
                select(RestaurantTable).where(
                    RestaurantTable.code == item["table_code"]
                )
            ).first()

            if not table:
                print(
                    f"Skipping reservation {item['id']}: "
                    f"table {item['table_code']} does not exist."
                )
                continue

            reservation = Reservation(
                id=item["id"],
                table_id=table.id,
                diner_id=item["diner_id"],
                party_size=item["party_size"],
                start_at=datetime.fromisoformat(item["start_at"]),
                end_at=datetime.fromisoformat(item["end_at"]),
                status=item["status"],
            )

            session.add(reservation)
            added += 1

        session.commit()

        print("Reservation seeding complete.")
        print(f"Added: {added}")
        print(f"Skipped: {skipped}")


if __name__ == "__main__":
    seed_reservations()
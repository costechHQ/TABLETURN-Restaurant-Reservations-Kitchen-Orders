import json

from pathlib import Path

from sqlmodel import Session, select

from app.db.session import engine
from app.models.table import RestaurantTable


TABLE_FILE = (
    Path(__file__).resolve().parents[2]
    / "app"
    / "data"
    / "restaurant_tables.json"
)


def seed_restaurant_tables():
    with open(TABLE_FILE, "r", encoding="utf-8") as file:
        tables = json.load(file)

    with Session(engine) as session:
        added = 0
        skipped = 0

        for item in tables:
            # Prevent duplicate restaurant tables
            existing_table = session.exec(
                select(RestaurantTable).where(
                    RestaurantTable.code == item["code"]
                )
            ).first()

            if existing_table:
                skipped += 1
                continue

            restaurant_table = RestaurantTable(
                code=item["code"],
                capacity=item["capacity"],
            )

            session.add(restaurant_table)
            added += 1

        session.commit()

        print("Restaurant table seeding complete.")
        print(f"Added: {added}")
        print(f"Skipped: {skipped}")


if __name__ == "__main__":
    seed_restaurant_tables()
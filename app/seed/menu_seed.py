import json
from decimal import Decimal
from pathlib import Path

from sqlmodel import Session, select

from app.db.session import engine
from app.models.menu_item import MenuItem



MENU_FILE = Path(__file__).resolve().parents[2]/ "app" / "data" / "menu_items.json"


def seed_menu_items():
    
    with open(MENU_FILE, "r", encoding="utf-8") as file:
        menu_items = json.load(file)

    with Session(engine) as session:
        added = 0
        skipped = 0

        for item in menu_items:
            # Prevent duplicate menu items
            existing_item = session.exec(
                select(MenuItem).where(MenuItem.name == item["name"])
            ).first()

            if existing_item:
                skipped += 1
                continue

            menu_item = MenuItem(
                name=item["name"],
                description=item["description"],
                price=Decimal(item["price"]),
                is_available=item.get("is_available", True),
            )

            session.add(menu_item)
            added += 1

        session.commit()

        print(f"Menu seeding complete.")
        print(f"Added: {added}")
        print(f"Skipped: {skipped}")


if __name__ == "__main__":
    seed_menu_items()


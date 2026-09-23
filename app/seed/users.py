import json

from pathlib import Path

from sqlmodel import Session, select

from app.db.session import engine
from app.models.user import User, UserRole


USERS_FILE = (
    Path(__file__).resolve().parents[2]
    / "app"
    / "data"
    / "users.json"
)


def seed_users():
    with open(USERS_FILE, "r", encoding="utf-8") as file:
        users = json.load(file)

    with Session(engine) as session:
        added = 0
        skipped = 0

        for item in users:
            # Prevent duplicate users
            existing_user = session.exec(
                select(User).where(User.id == item["id"])
            ).first()

            if existing_user:
                skipped += 1
                continue

            user = User(
                id=item["id"],
                email=item["email"],
                password_hash=item["password_hash"],
                role=UserRole(item["role"]),
            )

            session.add(user)
            added += 1

        session.commit()

        print("User seeding complete.")
        print(f"Added: {added}")
        print(f"Skipped: {skipped}")


if __name__ == "__main__":
    seed_users()

import sys

from sqlalchemy import select

from app.database import SessionLocal
from app.models import User


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python promote_admin.py email@example.com")
        raise SystemExit(1)

    email = sys.argv[1].strip().lower()

    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email))

        if user is None:
            print("User not found.")
            raise SystemExit(1)

        if user.role == "admin":
            print("This account is already an administrator.")
            return

        user.role = "admin"

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

        print("Administrator role assigned successfully.")


if __name__ == "__main__":
    main()

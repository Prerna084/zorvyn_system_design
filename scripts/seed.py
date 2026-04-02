"""
Create demo users and sample financial records. Safe to run multiple times:
skips users that already exist (by email).
"""

from datetime import date, timedelta

from sqlalchemy import select

from src.config.security import get_password_hash
from src.config.database import SessionLocal, engine
from src.config.database import Base
from src.models.record import EntryType, FinancialRecord
from src.models.user import User, UserRole


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        demo_users: list[tuple[str, str, str, UserRole]] = [
            ("admin@example.com", "admin12345", "Admin User", UserRole.ADMIN),
            ("analyst@example.com", "analyst12345", "Analyst User", UserRole.ANALYST),
            ("viewer@example.com", "viewer12345", "Viewer User", UserRole.VIEWER),
        ]
        email_to_user: dict[str, User] = {}
        for email, password, name, role in demo_users:
            existing = db.scalars(select(User).where(User.email == email)).first()
            if existing:
                email_to_user[email] = existing
                continue
            u = User(
                email=email,
                hashed_password=get_password_hash(password),
                full_name=name,
                role=role,
                is_active=True,
            )
            db.add(u)
            db.commit()
            db.refresh(u)
            email_to_user[email] = u

        admin = email_to_user["admin@example.com"]
        has_any = db.scalars(select(FinancialRecord).limit(1)).first()
        if has_any is None:
            # no rows - add sample data
            today = date.today()
            samples = [
                (1200.0, EntryType.INCOME, "Salary", today.replace(day=1)),
                (45.5, EntryType.EXPENSE, "Food", today - timedelta(days=2)),
                (200.0, EntryType.INCOME, "Freelance", today - timedelta(days=5)),
                (80.0, EntryType.EXPENSE, "Transport", today - timedelta(days=3)),
                (300.0, EntryType.EXPENSE, "Rent", today - timedelta(days=10)),
            ]
            for amt, et, cat, d in samples:
                db.add(
                    FinancialRecord(
                        amount=amt,
                        type=et,
                        category=cat,
                        entry_date=d,
                        notes="Sample seed data",
                        created_by_id=admin.id,
                    )
                )
            db.commit()
        print("Seed complete. Demo logins:")
        print("  admin@example.com / admin12345")
        print("  analyst@example.com / analyst12345")
        print("  viewer@example.com / viewer12345")
    finally:
        db.close()


if __name__ == "__main__":
    seed()

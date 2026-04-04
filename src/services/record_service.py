from datetime import UTC, date, datetime

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from src.models.record import EntryType, FinancialRecord
from src.validations.record import FinancialRecordCreate, FinancialRecordUpdate


def list_records_service(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    type: EntryType | None = None,
    category: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    q: str | None = None,
) -> list[FinancialRecord]:
    stmt = select(FinancialRecord).where(FinancialRecord.deleted_at.is_(None))
    if type is not None:
        stmt = stmt.where(FinancialRecord.type == type)
    if category:
        stmt = stmt.where(FinancialRecord.category == category)
    if date_from is not None:
        stmt = stmt.where(FinancialRecord.entry_date >= date_from)
    if date_to is not None:
        stmt = stmt.where(FinancialRecord.entry_date <= date_to)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(FinancialRecord.category.ilike(like), FinancialRecord.notes.ilike(like)))
    stmt = stmt.order_by(FinancialRecord.entry_date.desc(), FinancialRecord.id.desc()).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def get_record_service(db: Session, record_id: int) -> FinancialRecord | None:
    rec = db.get(FinancialRecord, record_id)
    if not rec or rec.deleted_at is not None:
        return None
    return rec


def create_record_service(db: Session, body: FinancialRecordCreate, user_id: int) -> FinancialRecord:
    rec = FinancialRecord(
        amount=body.amount,
        type=body.type,
        category=body.category.strip(),
        entry_date=body.entry_date,
        notes=body.notes,
        created_by_id=user_id,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


def update_record_service(
    db: Session, record_id: int, body: FinancialRecordUpdate
) -> FinancialRecord | None:
    rec = db.get(FinancialRecord, record_id)
    if not rec or rec.deleted_at is not None:
        return None
        
    data = body.dict(exclude_unset=True)
    if "category" in data and data["category"] is not None:
        data["category"] = data["category"].strip()
    for k, v in data.items():
        setattr(rec, k, v)
    rec.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(rec)
    return rec


def delete_record_service(db: Session, record_id: int) -> bool:
    rec = db.get(FinancialRecord, record_id)
    if not rec or rec.deleted_at is not None:
        return False
    rec.deleted_at = datetime.now(UTC)
    db.commit()
    return True

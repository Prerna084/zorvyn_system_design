from datetime import UTC, datetime, date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.deps import RequireAdmin, RequireAnyAuthenticated
from app.database import get_db
from app.models import EntryType, FinancialRecord
from app.schemas.finance import FinancialRecordCreate, FinancialRecordOut, FinancialRecordUpdate

router = APIRouter()


@router.get("", response_model=list[FinancialRecordOut])
def list_records(
    _: RequireAnyAuthenticated,
    db: Annotated[Session, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    type: Annotated[EntryType | None, Query(description="Filter by income or expense")] = None,
    category: Annotated[str | None, Query()] = None,
    date_from: Annotated[date | None, Query()] = None,
    date_to: Annotated[date | None, Query()] = None,
    q: Annotated[str | None, Query(description="Search in category and notes")] = None,
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


@router.get("/{record_id}", response_model=FinancialRecordOut)
def get_record(
    record_id: int,
    _: RequireAnyAuthenticated,
    db: Annotated[Session, Depends(get_db)],
) -> FinancialRecord:
    rec = db.get(FinancialRecord, record_id)
    if not rec or rec.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return rec


@router.post("", response_model=FinancialRecordOut, status_code=status.HTTP_201_CREATED)
def create_record(
    body: FinancialRecordCreate,
    current: RequireAdmin,
    db: Annotated[Session, Depends(get_db)],
) -> FinancialRecord:
    rec = FinancialRecord(
        amount=body.amount,
        type=body.type,
        category=body.category.strip(),
        entry_date=body.entry_date,
        notes=body.notes,
        created_by_id=current.id,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


@router.patch("/{record_id}", response_model=FinancialRecordOut)
def update_record(
    record_id: int,
    body: FinancialRecordUpdate,
    _: RequireAdmin,
    db: Annotated[Session, Depends(get_db)],
) -> FinancialRecord:
    rec = db.get(FinancialRecord, record_id)
    if not rec or rec.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    data = body.model_dump(exclude_unset=True)
    if "category" in data and data["category"] is not None:
        data["category"] = data["category"].strip()
    for k, v in data.items():
        setattr(rec, k, v)
    rec.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(rec)
    return rec


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(
    record_id: int,
    _: RequireAdmin,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    rec = db.get(FinancialRecord, record_id)
    if not rec or rec.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    rec.deleted_at = datetime.now(UTC)
    db.commit()

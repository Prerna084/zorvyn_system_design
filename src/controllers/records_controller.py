from datetime import date
from typing import Annotated
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from src.middlewares.auth import RequireAdmin, RequireAnyAuthenticated
from src.config.database import get_db
from src.models.record import EntryType, FinancialRecord
from src.validations.record import FinancialRecordCreate, FinancialRecordOut, FinancialRecordUpdate
from src.services import record_service

def list_records(
    _: RequireAnyAuthenticated,
    db: Annotated[Session, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    type: Annotated[EntryType | None, Query()] = None,
    category: Annotated[str | None, Query()] = None,
    date_from: Annotated[date | None, Query()] = None,
    date_to: Annotated[date | None, Query()] = None,
    q: Annotated[str | None, Query()] = None,
) -> list[FinancialRecord]:
    return record_service.list_records_service(db, skip, limit, type, category, date_from, date_to, q)

def get_record(
    record_id: int,
    _: RequireAnyAuthenticated,
    db: Annotated[Session, Depends(get_db)],
) -> FinancialRecord:
    rec = record_service.get_record_service(db, record_id)
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return rec

def create_record(
    body: FinancialRecordCreate,
    current: RequireAdmin,
    db: Annotated[Session, Depends(get_db)],
) -> FinancialRecord:
    return record_service.create_record_service(db, body, current.id)

def update_record(
    record_id: int,
    body: FinancialRecordUpdate,
    _: RequireAdmin,
    db: Annotated[Session, Depends(get_db)],
) -> FinancialRecord:
    rec = record_service.update_record_service(db, record_id, body)
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return rec

def delete_record(
    record_id: int,
    _: RequireAdmin,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    success = record_service.delete_record_service(db, record_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies.auth import RequireAdmin, RequireAnyAuthenticated
from app.database import get_db
from app.models.record import EntryType, FinancialRecord
from app.schemas.record import FinancialRecordCreate, FinancialRecordOut, FinancialRecordUpdate
from app.services import record_service

router = APIRouter()


@router.get("", response_model=list[FinancialRecordOut])
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


@router.get("/{record_id}", response_model=FinancialRecordOut)
def get_record(
    record_id: int,
    _: RequireAnyAuthenticated,
    db: Annotated[Session, Depends(get_db)],
) -> FinancialRecord:
    rec = record_service.get_record_service(db, record_id)
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return rec


@router.post("", response_model=FinancialRecordOut, status_code=status.HTTP_201_CREATED)
def create_record(
    body: FinancialRecordCreate,
    current: RequireAdmin,
    db: Annotated[Session, Depends(get_db)],
) -> FinancialRecord:
    return record_service.create_record_service(db, body, current.id)


@router.patch("/{record_id}", response_model=FinancialRecordOut)
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


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(
    record_id: int,
    _: RequireAdmin,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    success = record_service.delete_record_service(db, record_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")

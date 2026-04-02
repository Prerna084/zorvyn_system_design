from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.record import EntryType


class FinancialRecordCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Positive amount in account currency")
    type: EntryType
    category: str = Field(..., min_length=1, max_length=128)
    entry_date: date
    notes: str | None = Field(None, max_length=4000)


class FinancialRecordUpdate(BaseModel):
    amount: float | None = Field(None, gt=0)
    type: EntryType | None = None
    category: str | None = Field(None, min_length=1, max_length=128)
    entry_date: date | None = None
    notes: str | None = Field(None, max_length=4000)


class FinancialRecordOut(BaseModel):
    id: int
    amount: float
    type: EntryType
    category: str
    entry_date: date
    notes: str | None
    created_by_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RecentActivityItem(BaseModel):
    id: int
    amount: float
    type: EntryType
    category: str
    entry_date: date
    created_at: datetime


class CategoryTotal(BaseModel):
    category: str
    income: float
    expense: float
    net: float


class PeriodTrend(BaseModel):
    period_start: date
    period_label: str
    income: float
    expense: float
    net: float


class DashboardSummary(BaseModel):
    date_from: date | None
    date_to: date | None
    total_income: float
    total_expense: float
    net_balance: float
    category_totals: list[CategoryTotal]
    recent_activity: list[RecentActivityItem]
    weekly_trends: list[PeriodTrend]
    monthly_trends: list[PeriodTrend]

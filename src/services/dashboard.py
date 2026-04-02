from collections import defaultdict
from collections.abc import Sequence
from datetime import date, timedelta
from typing import Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.record import EntryType, FinancialRecord
from src.validations.record import (
    CategoryTotal,
    DashboardSummary,
    PeriodTrend,
    RecentActivityItem,
)


def _period_start(d: date, granularity: Literal["week", "month"]) -> date:
    if granularity == "month":
        return date(d.year, d.month, 1)
    # ISO week: Monday start
    return d - timedelta(days=d.weekday())


def build_dashboard_summary(
    db: Session,
    date_from: date | None,
    date_to: date | None,
    recent_limit: int = 10,
) -> DashboardSummary:
    q = select(FinancialRecord).where(FinancialRecord.deleted_at.is_(None))
    if date_from is not None:
        q = q.where(FinancialRecord.entry_date >= date_from)
    if date_to is not None:
        q = q.where(FinancialRecord.entry_date <= date_to)

    rows: Sequence[FinancialRecord] = list(db.scalars(q.order_by(FinancialRecord.entry_date.desc())).all())

    total_income = 0.0
    total_expense = 0.0
    cat_income: dict[str, float] = defaultdict(float)
    cat_expense: dict[str, float] = defaultdict(float)

    week_buckets: dict[date, tuple[float, float]] = defaultdict(lambda: (0.0, 0.0))
    month_buckets: dict[date, tuple[float, float]] = defaultdict(lambda: (0.0, 0.0))

    for r in rows:
        if r.type == EntryType.INCOME:
            total_income += r.amount
            cat_income[r.category] += r.amount
        else:
            total_expense += r.amount
            cat_expense[r.category] += r.amount

        ws = _period_start(r.entry_date, "week")
        ms = _period_start(r.entry_date, "month")
        wi, we = week_buckets[ws]
        mi, me = month_buckets[ms]
        if r.type == EntryType.INCOME:
            week_buckets[ws] = (wi + r.amount, we)
            month_buckets[ms] = (mi + r.amount, me)
        else:
            week_buckets[ws] = (wi, we + r.amount)
            month_buckets[ms] = (mi, me + r.amount)

    categories = set(cat_income) | set(cat_expense)
    category_totals: list[CategoryTotal] = []
    for c in sorted(categories):
        inc = cat_income.get(c, 0.0)
        exp = cat_expense.get(c, 0.0)
        category_totals.append(CategoryTotal(category=c, income=inc, expense=exp, net=inc - exp))

    recent_q = select(FinancialRecord).where(FinancialRecord.deleted_at.is_(None))
    if date_from is not None:
        recent_q = recent_q.where(FinancialRecord.entry_date >= date_from)
    if date_to is not None:
        recent_q = recent_q.where(FinancialRecord.entry_date <= date_to)
    recent_q = recent_q.order_by(FinancialRecord.created_at.desc()).limit(recent_limit)

    recent_rows = list(db.scalars(recent_q).all())
    recent_activity = [
        RecentActivityItem(
            id=x.id,
            amount=x.amount,
            type=x.type,
            category=x.category,
            entry_date=x.entry_date,
            created_at=x.created_at,
        )
        for x in recent_rows
    ]

    def trends_from_buckets(buckets: dict[date, tuple[float, float]], label_fmt: str) -> list[PeriodTrend]:
        out: list[PeriodTrend] = []
        for start in sorted(buckets.keys()):
            inc, exp = buckets[start]
            out.append(
                PeriodTrend(
                    period_start=start,
                    period_label=start.strftime(label_fmt),
                    income=inc,
                    expense=exp,
                    net=inc - exp,
                )
            )
        return out

    weekly_trends = trends_from_buckets(week_buckets, "%Y-%m-%d")
    monthly_trends = trends_from_buckets(month_buckets, "%Y-%m")

    return DashboardSummary(
        date_from=date_from,
        date_to=date_to,
        total_income=total_income,
        total_expense=total_expense,
        net_balance=total_income - total_expense,
        category_totals=category_totals,
        recent_activity=recent_activity,
        weekly_trends=weekly_trends,
        monthly_trends=monthly_trends,
    )

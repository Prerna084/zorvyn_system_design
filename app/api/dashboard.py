from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies.auth import RequireAnalystOrAdmin
from app.database import get_db
from app.schemas.record import DashboardSummary
from app.services.dashboard import build_dashboard_summary

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(
    _: RequireAnalystOrAdmin,
    db: Annotated[Session, Depends(get_db)],
    date_from: Annotated[date | None, Query()] = None,
    date_to: Annotated[date | None, Query()] = None,
    recent_limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> DashboardSummary:
    """
    Aggregated metrics for the finance dashboard. Available to Analyst and Admin roles.
    Viewers do not have access to the dashboard in this configuration.
    """
    return build_dashboard_summary(db, date_from=date_from, date_to=date_to, recent_limit=recent_limit)

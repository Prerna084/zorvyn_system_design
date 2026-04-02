from datetime import date
from typing import Annotated
from fastapi import Depends, Query
from sqlalchemy.orm import Session
from src.middlewares.auth import RequireAnalystOrAdmin
from src.config.database import get_db
from src.validations.record import DashboardSummary
from src.services.dashboard import build_dashboard_summary

def dashboard_summary(
    _: RequireAnalystOrAdmin,
    db: Annotated[Session, Depends(get_db)],
    date_from: Annotated[date | None, Query()] = None,
    date_to: Annotated[date | None, Query()] = None,
    recent_limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> DashboardSummary:
    return build_dashboard_summary(db, date_from=date_from, date_to=date_to, recent_limit=recent_limit)

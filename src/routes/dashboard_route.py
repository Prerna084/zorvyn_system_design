from fastapi import APIRouter
from src.controllers import dashboard_controller
from src.validations.record import DashboardSummary

router = APIRouter()
router.get("/summary", response_model=DashboardSummary)(dashboard_controller.dashboard_summary)

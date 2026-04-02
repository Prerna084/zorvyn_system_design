from fastapi import APIRouter, status
from src.controllers import records_controller
from src.validations.record import FinancialRecordOut

router = APIRouter()
router.get("", response_model=list[FinancialRecordOut])(records_controller.list_records)
router.get("/{record_id}", response_model=FinancialRecordOut)(records_controller.get_record)
router.post("", response_model=FinancialRecordOut, status_code=status.HTTP_201_CREATED)(records_controller.create_record)
router.patch("/{record_id}", response_model=FinancialRecordOut)(records_controller.update_record)
router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)(records_controller.delete_record)

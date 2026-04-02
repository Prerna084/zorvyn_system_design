from fastapi import APIRouter, status
from src.controllers import users_controller
from src.validations.user import UserOut

router = APIRouter()
router.get("", response_model=list[UserOut])(users_controller.list_users)
router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)(users_controller.create_user)
router.get("/{user_id}", response_model=UserOut)(users_controller.get_user)
router.patch("/{user_id}", response_model=UserOut)(users_controller.update_user)
router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)(users_controller.deactivate_user)

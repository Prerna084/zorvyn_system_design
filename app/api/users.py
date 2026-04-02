from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies.auth import RequireAdmin, RequireAnyAuthenticated, get_current_user
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserOut, UserUpdate
from app.services import user_service

router = APIRouter()


@router.get("", response_model=list[UserOut])
def list_users(
    _: RequireAdmin,
    db: Annotated[Session, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[User]:
    return user_service.list_users_service(db, skip, limit)


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    body: UserCreate,
    _: RequireAdmin,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if user_service.get_user_by_email_service(db, body.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    return user_service.create_user_service(db, body)


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    current: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if current.role != UserRole.ADMIN and current.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to view this user")
    user = user_service.get_user_service(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    body: UserUpdate,
    _: RequireAdmin,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    user = user_service.update_user_service(db, user_id, body)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_user(
    user_id: int,
    current: RequireAdmin,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    if user_id == current.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot deactivate yourself")
    success = user_service.deactivate_user_service(db, user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

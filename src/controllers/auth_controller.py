from datetime import timedelta
from typing import Annotated
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from src.middlewares.auth import get_current_user
from src.config.security import create_access_token, verify_password
from src.config.database import get_db
from src.models.user import User
from src.validations.auth import Token
from src.validations.user import UserOut

def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")
    token = create_access_token(subject=user.email, user_id=user.id)
    return Token(access_token=token)

def me(current: Annotated[User, Depends(get_current_user)]) -> User:
    return current

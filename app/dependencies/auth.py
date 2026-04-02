from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import safe_decode_token
from app.database import get_db
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token", auto_error=False)


def get_current_user_optional(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User | None:
    if not token:
        return None
    payload = safe_decode_token(token)
    if not payload or payload.get("user_id") is None:
        return None
    user = db.get(User, int(payload["user_id"]))
    if not user or not user.is_active:
        return None
    return user


def get_current_user(
    user: Annotated[User | None, Depends(get_current_user_optional)],
) -> User:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_roles(*allowed: UserRole) -> Callable[..., User]:
    def checker(current: Annotated[User, Depends(get_current_user)]) -> User:
        if current.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for this action",
            )
        return current

    return checker


RequireAdmin = Annotated[User, Depends(require_roles(UserRole.ADMIN))]
RequireAnalystOrAdmin = Annotated[User, Depends(require_roles(UserRole.ANALYST, UserRole.ADMIN))]
RequireAnyAuthenticated = Annotated[User, Depends(get_current_user)]

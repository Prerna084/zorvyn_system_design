import os

os.makedirs('src/controllers', exist_ok=True)
os.makedirs('src/routes', exist_ok=True)

# ----------------------------------------------------
# 1. USERS
# ----------------------------------------------------
user_controller = """from typing import Annotated
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from src.middlewares.auth import RequireAdmin, RequireAnyAuthenticated, get_current_user
from src.config.database import get_db
from src.models.user import User, UserRole
from src.validations.user import UserCreate, UserOut, UserUpdate
from src.services import user_service

def list_users(
    _: RequireAdmin,
    db: Annotated[Session, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[User]:
    return user_service.list_users_service(db, skip, limit)

def create_user(
    body: UserCreate,
    _: RequireAdmin,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if user_service.get_user_by_email_service(db, body.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    return user_service.create_user_service(db, body)

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
"""

user_route = """from fastapi import APIRouter, status
from src.controllers import users_controller
from src.validations.user import UserOut

router = APIRouter()
router.get("", response_model=list[UserOut])(users_controller.list_users)
router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)(users_controller.create_user)
router.get("/{user_id}", response_model=UserOut)(users_controller.get_user)
router.patch("/{user_id}", response_model=UserOut)(users_controller.update_user)
router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)(users_controller.deactivate_user)
"""

with open('src/controllers/users_controller.py', 'w') as f: f.write(user_controller)
with open('src/routes/users_route.py', 'w') as f: f.write(user_route)

# ----------------------------------------------------
# 2. RECORDS
# ----------------------------------------------------
record_controller = """from datetime import date
from typing import Annotated
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from src.middlewares.auth import RequireAdmin, RequireAnyAuthenticated
from src.config.database import get_db
from src.models.record import EntryType, FinancialRecord
from src.validations.record import FinancialRecordCreate, FinancialRecordOut, FinancialRecordUpdate
from src.services import record_service

def list_records(
    _: RequireAnyAuthenticated,
    db: Annotated[Session, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    type: Annotated[EntryType | None, Query()] = None,
    category: Annotated[str | None, Query()] = None,
    date_from: Annotated[date | None, Query()] = None,
    date_to: Annotated[date | None, Query()] = None,
    q: Annotated[str | None, Query()] = None,
) -> list[FinancialRecord]:
    return record_service.list_records_service(db, skip, limit, type, category, date_from, date_to, q)

def get_record(
    record_id: int,
    _: RequireAnyAuthenticated,
    db: Annotated[Session, Depends(get_db)],
) -> FinancialRecord:
    rec = record_service.get_record_service(db, record_id)
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return rec

def create_record(
    body: FinancialRecordCreate,
    current: RequireAdmin,
    db: Annotated[Session, Depends(get_db)],
) -> FinancialRecord:
    return record_service.create_record_service(db, body, current.id)

def update_record(
    record_id: int,
    body: FinancialRecordUpdate,
    _: RequireAdmin,
    db: Annotated[Session, Depends(get_db)],
) -> FinancialRecord:
    rec = record_service.update_record_service(db, record_id, body)
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return rec

def delete_record(
    record_id: int,
    _: RequireAdmin,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    success = record_service.delete_record_service(db, record_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
"""

record_route = """from fastapi import APIRouter, status
from src.controllers import records_controller
from src.validations.record import FinancialRecordOut

router = APIRouter()
router.get("", response_model=list[FinancialRecordOut])(records_controller.list_records)
router.get("/{record_id}", response_model=FinancialRecordOut)(records_controller.get_record)
router.post("", response_model=FinancialRecordOut, status_code=status.HTTP_201_CREATED)(records_controller.create_record)
router.patch("/{record_id}", response_model=FinancialRecordOut)(records_controller.update_record)
router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)(records_controller.delete_record)
"""

with open('src/controllers/records_controller.py', 'w') as f: f.write(record_controller)
with open('src/routes/records_route.py', 'w') as f: f.write(record_route)


# ----------------------------------------------------
# 3. DASHBOARD
# ----------------------------------------------------
dashboard_controller = """from datetime import date
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
"""

dashboard_route = """from fastapi import APIRouter
from src.controllers import dashboard_controller
from src.validations.record import DashboardSummary

router = APIRouter()
router.get("/summary", response_model=DashboardSummary)(dashboard_controller.dashboard_summary)
"""

with open('src/controllers/dashboard_controller.py', 'w') as f: f.write(dashboard_controller)
with open('src/routes/dashboard_route.py', 'w') as f: f.write(dashboard_route)


# ----------------------------------------------------
# 4. AUTH
# ----------------------------------------------------
auth_controller = """from datetime import timedelta
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
"""

auth_route = """from fastapi import APIRouter
from src.controllers import auth_controller
from src.validations.auth import Token
from src.validations.user import UserOut
from src.main import limiter

router = APIRouter()

# Decorator must be applied directly to the handler or wrapped here.
# FastAPI limiter can take the path, so we use limit on the actual function route.
# Alternatively, wrap it.
_login = limiter.limit("5/minute")(auth_controller.login)
router.post("/token", response_model=Token)(_login)

router.get("/me", response_model=UserOut)(auth_controller.me)
"""

with open('src/controllers/auth_controller.py', 'w') as f: f.write(auth_controller)
with open('src/routes/auth_route.py', 'w') as f: f.write(auth_route)


# ----------------------------------------------------
# 5. INDEX ROUTER (routes/index.py)
# ----------------------------------------------------
index_route = """from fastapi import APIRouter
from src.routes.auth_route import router as auth_router
from src.routes.users_route import router as users_router
from src.routes.records_route import router as records_router
from src.routes.dashboard_route import router as dashboard_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(records_router, prefix="/records", tags=["records"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
"""

with open('src/routes/index.py', 'w') as f: f.write(index_route)
with open('src/controllers/__init__.py', 'w') as f: f.write("")
with open('src/routes/__init__.py', 'w') as f: f.write("")

# Update main.py
with open('src/main.py', 'r') as f:
    main_content = f.read()

main_content = main_content.replace('from src.api.routes import api_router', 'from src.routes.index import api_router')
with open('src/main.py', 'w') as f:
    f.write(main_content)

print("done")

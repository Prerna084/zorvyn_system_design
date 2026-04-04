from sqlalchemy.orm import Session
from src.models.user import User
from src.config.security import get_password_hash
from src.validations.user import UserCreate, UserUpdate


def list_users_service(db: Session, skip: int = 0, limit: int = 50) -> list[User]:
    return list(db.query(User).order_by(User.id).offset(skip).limit(limit).all())


def get_user_by_email_service(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user_service(db: Session, body: UserCreate) -> User:
    user = User(
        email=body.email,
        hashed_password=get_password_hash(body.password),
        full_name=body.full_name,
        role=body.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_service(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def update_user_service(db: Session, user_id: int, body: UserUpdate) -> User | None:
    user = db.get(User, user_id)
    if not user:
        return None
        
    data = body.dict(exclude_unset=True)
    if "password" in data:
        data["hashed_password"] = get_password_hash(data.pop("password"))
    for k, v in data.items():
        setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return user


def deactivate_user_service(db: Session, user_id: int) -> bool:
    user = db.get(User, user_id)
    if not user:
        return False
    user.is_active = False
    db.commit()
    return True

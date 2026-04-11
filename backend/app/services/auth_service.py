import secrets

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, SignupRequest


def create_user(db: Session, payload: SignupRequest) -> User:
    user = User(
        name=payload.name,
        email=payload.email.lower(),
        password_hash=get_password_hash(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, payload: LoginRequest) -> User | None:
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        return None
    return user


def get_or_create_oauth_user(db: Session, *, email: str, name: str) -> User:
    user = db.query(User).filter(User.email == email.lower()).first()
    if user:
        if name and user.name != name:
            user.name = name
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    user = User(
        name=name,
        email=email.lower(),
        password_hash=get_password_hash(secrets.token_urlsafe(32)),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

"""Repository encapsulating all persistence logic for users."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import UserCreate


class UserRepository:
    """Thin data-access layer providing focused operations."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_email(self, email: str) -> User | None:
        return self._db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> User | None:
        return self._db.query(User).filter(User.username == username).first()

    def get_by_identifier(self, identifier: str) -> User | None:
        query = self._db.query(User).filter((User.username == identifier) | (User.email == identifier))
        return query.first()

    def create(self, payload: UserCreate, hashed_password: str) -> User:
        new_user = User(
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            phone=payload.phone,
            contact=payload.contact,
            short_description=payload.short_description,
            username=payload.username,
            hashed_password=hashed_password,
        )
        self._db.add(new_user)
        self._db.commit()
        self._db.refresh(new_user)
        return new_user

    def update_password(self, user: User, hashed_password: str) -> User:
        user.hashed_password = hashed_password
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user

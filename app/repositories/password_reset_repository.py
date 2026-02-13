"""Repository handling password reset token persistence."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload

from app.models.password_reset_token import PasswordResetToken


class PasswordResetRepository:
    """Encapsulates CRUD operations for password reset tokens."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, user_id: int, token_hash: str, expires_at: datetime) -> PasswordResetToken:
        token = PasswordResetToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
        self._db.add(token)
        self._db.commit()
        self._db.refresh(token)
        return token

    def remove_active_tokens_for_user(self, user_id: int) -> None:
        self._db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.used.is_(False),
        ).delete(synchronize_session=False)
        self._db.commit()

    def get_by_hash(self, token_hash: str) -> PasswordResetToken | None:
        return (
            self._db.query(PasswordResetToken)
            .options(joinedload(PasswordResetToken.user))
            .filter(PasswordResetToken.token_hash == token_hash)
            .first()
        )

    def mark_used(self, token: PasswordResetToken) -> PasswordResetToken:
        token.used = True
        token.used_at = datetime.now(timezone.utc)
        self._db.add(token)
        self._db.commit()
        self._db.refresh(token)
        return token
*** End Patch
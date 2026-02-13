"""Domain logic for authentication workflows."""
from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status

from app.core.config import get_settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.repositories.password_reset_repository import PasswordResetRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserCreate,
)
from app.services.email_service import EmailService


class AuthService:
    """Coordinates repositories, security helpers, and messaging gateways."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_reset_repository: PasswordResetRepository,
        email_service: EmailService,
    ) -> None:
        self._user_repository = user_repository
        self._password_reset_repository = password_reset_repository
        self._email_service = email_service
        self._settings = get_settings()

    def register_user(self, payload: UserCreate) -> User:
        if self._user_repository.get_by_email(payload.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="email is already registered",
            )
        if self._user_repository.get_by_username(payload.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="username is already taken",
            )

        hashed_password = get_password_hash(payload.password)
        return self._user_repository.create(payload, hashed_password)

    def authenticate_user(self, payload: LoginRequest) -> TokenResponse:
        user = self._user_repository.get_by_identifier(payload.identifier)
        if not user or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid credentials",
            )
        token = create_access_token(str(user.id))
        return TokenResponse(access_token=token)

    def request_password_reset(self, payload: ForgotPasswordRequest) -> None:
        user = self._user_repository.get_by_identifier(payload.identifier)
        if not user:
            return

        self._password_reset_repository.remove_active_tokens_for_user(user.id)
        token_value = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token_value.encode()).hexdigest()
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=self._settings.password_reset_token_expire_minutes
        )
        self._password_reset_repository.create(user.id, token_hash, expires_at)
        self._email_service.send_password_reset(user.email, token_value, user.first_name)

    def reset_password(self, payload: ResetPasswordRequest) -> None:
        token_hash = hashlib.sha256(payload.token.encode()).hexdigest()
        token = self._password_reset_repository.get_by_hash(token_hash)
        if not token or token.used or token.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="invalid or expired reset token",
            )

        hashed_password = get_password_hash(payload.new_password)
        self._user_repository.update_password(token.user, hashed_password)
        self._password_reset_repository.mark_used(token)

"""Controller translating transport concerns to domain services."""
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    ResetPasswordRequest,
    TokenResponse,
    UserCreate,
    UserRead,
)
from app.services.auth_service import AuthService


class AuthController:
    """Expose high-level orchestration methods used by routers."""

    def __init__(self, service: AuthService) -> None:
        self._service = service

    def register(self, payload: UserCreate) -> UserRead:
        user = self._service.register_user(payload)
        return UserRead.model_validate(user)

    def login(self, payload: LoginRequest) -> TokenResponse:
        return self._service.authenticate_user(payload)

    def forgot_password(self, payload: ForgotPasswordRequest) -> MessageResponse:
        self._service.request_password_reset(payload)
        return MessageResponse(message="If the account exists, a reset email has been sent.")

    def reset_password(self, payload: ResetPasswordRequest) -> MessageResponse:
        self._service.reset_password(payload)
        return MessageResponse(message="Password updated successfully.")

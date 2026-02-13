"""API routes for authentication workflows."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.controllers.auth_controller import AuthController
from app.db.session import get_db
from app.repositories.password_reset_repository import PasswordResetRepository
from app.repositories.user_repository import UserRepository
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
from app.services.email_service import EmailService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_controller(db: Session = Depends(get_db)) -> AuthController:
    user_repository = UserRepository(db)
    password_reset_repository = PasswordResetRepository(db)
    email_service = EmailService()
    service = AuthService(user_repository, password_reset_repository, email_service)
    return AuthController(service)


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(
    payload: UserCreate, controller: AuthController = Depends(get_auth_controller)
) -> UserRead:
    return controller.register(payload)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, controller: AuthController = Depends(get_auth_controller)) -> TokenResponse:
    return controller.login(payload)


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def forgot_password(
    payload: ForgotPasswordRequest,
    controller: AuthController = Depends(get_auth_controller),
) -> MessageResponse:
    return controller.forgot_password(payload)


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(
    payload: ResetPasswordRequest,
    controller: AuthController = Depends(get_auth_controller),
) -> MessageResponse:
    return controller.reset_password(payload)

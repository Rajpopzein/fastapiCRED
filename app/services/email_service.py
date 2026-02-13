"""Simple SMTP email delivery helper."""
from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


class EmailService:
    """Responsible for composing and dispatching transactional emails."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def send_password_reset(self, recipient: str, token: str, recipient_name: str | None = None) -> None:
        reset_link = f"{self._settings.password_reset_base_url}?token={token}"
        subject = f"Reset your {self._settings.project_name} password"
        greeting_name = recipient_name or "there"
        body = (
            f"Hi {greeting_name},\n\n"
            "We received a request to reset the password to your account.\n"
            "Use the secure link below to choose a new password. The link expires soon.\n\n"
            f"Reset password: {reset_link}\n\n"
            "If you did not request this change you can safely ignore this email."
        )

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self._settings.smtp_sender
        message["To"] = recipient
        message.set_content(body)

        if self._settings.smtp_suppress_send:
            logger.info("SMTP send suppressed. Token for %s would be %s", recipient, token)
            return

        with smtplib.SMTP(self._settings.smtp_host, self._settings.smtp_port) as smtp:
            if self._settings.smtp_use_tls:
                smtp.starttls()
            if self._settings.smtp_username and self._settings.smtp_password:
                smtp.login(self._settings.smtp_username, self._settings.smtp_password)
            smtp.send_message(message)

"""FastAPI application entrypoint."""
from fastapi import FastAPI

from app.core.config import get_settings
from app.db import base  # noqa: F401 -- ensures models are imported for Alembic
from app.db.session import Base, engine
from app.routers.auth_router import router as auth_router

settings = get_settings()


def create_app() -> FastAPI:
    """Build and configure the FastAPI application instance."""
    application = FastAPI(title=settings.project_name, version="1.0.0")
    application.include_router(auth_router, prefix=settings.api_prefix)

    @application.get("/health", tags=["health"])
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return application


# Create database tables during startup for simple deployments.
Base.metadata.create_all(bind=engine)

app = create_app()

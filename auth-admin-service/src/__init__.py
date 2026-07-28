"""FastAPI app for the auth service (migrated from Flask/flask-openapi3)."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from gmsshared.src.config import get_config
from gmsshared import celery
from gmsshared.src.web.fastapi_glue import (
    install_session_middleware,
    install_exception_handlers,
)


def _configure_celery():
    env = get_config().ENV
    email_queue = f"'{env}-gms:emails'"
    celery.conf.update(
        task_serializer="json",
        result_serializer="json",
        enable_utc=True,
        broker_connection_retry_on_startup=True,
        task_routes={
            "owner_verification_email": {"queue": email_queue},
            "staff_account_verification_email": {"queue": email_queue},
            "staff_password_reset_email": {"queue": email_queue},
            "owner_onboard_admin_email": {"queue": email_queue},
            "contact_app_verification_code_email": {"queue": email_queue},
            "contact_app_forgotten_password_code_email": {"queue": email_queue},
            "profile_setup_email": {"queue": email_queue},
        },
    )


def create_app() -> FastAPI:
    app = FastAPI(title="GMS Auth API", version="1.1")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    install_session_middleware(app)
    install_exception_handlers(app)
    _configure_celery()

    from auth_admin_service import auth_bp

    app.include_router(auth_bp)
    return app


app = create_app()

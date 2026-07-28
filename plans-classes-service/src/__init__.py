"""FastAPI app for the plans and payments service (migrated from Flask/flask-openapi3)."""
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
    batch_queue = f"'{env}-gms:batch-queue'"
    celery.conf.update(
        task_serializer="json",
        result_serializer="json",
        enable_utc=True,
        broker_connection_retry_on_startup=True,
        task_routes={
            "booking_cancellation_email": {"queue": email_queue},
            "updated_session_email": {"queue": email_queue},
            "create_single_session_pt_email": {"queue": email_queue},
            "create_recurring_session_pt_email": {"queue": email_queue},
            "updated_single_session_pt_email": {"queue": email_queue},
            "updated_recurring_session_pt_email": {"queue": email_queue},
            "session_cancellation_pt_coach_email": {"queue": email_queue},
            "session_cancellation_pt_member_email": {"queue": email_queue},
            "add_to_waitlist_email": {"queue": email_queue},
            "promote_waitlist_to_registered_email": {"queue": email_queue},
            "update_group": {"queue": batch_queue},
            "update_members_to_group": {"queue": batch_queue},
        },
    )


def create_app() -> FastAPI:
    app = FastAPI(title="GMS Plans and Payments API", version="1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    install_session_middleware(app)
    install_exception_handlers(app)
    _configure_celery()

    from plans_classes_service import plans_classes_api

    app.include_router(plans_classes_api)
    return app


app = create_app()

"""FastAPI app for the members service (migrated from Flask/flask-openapi3)."""
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
    payments_queue = f"'{env}-gms:payments'"
    door_access_queue = f"'{env}-gms:door_access'"
    batch_queue = f"'{env}-gms:batch-queue'"

    celery.conf.update(
        task_serializer="json",
        result_serializer="json",
        enable_utc=True,
        broker_connection_retry_on_startup=True,
        task_routes={
            "contact_app_download_link_email": {"queue": email_queue},
            "onboard_member_in_payrix": {"queue": payments_queue},
            "tokenize_ach_for_customer": {"queue": payments_queue},
            "process_membership": {"queue": payments_queue},
            "retry_payment": {"queue": payments_queue},
            "process_payment": {"queue": payments_queue},
            "process_payment_v2": {"queue": payments_queue},
            "refund_payment": {"queue": payments_queue},
            "refund_payment_v2": {"queue": payments_queue},
            "delete_token": {"queue": payments_queue},
            "update_zipcode": {"queue": payments_queue},
            "profile_setup_email": {"queue": email_queue},
            "door_access_member_login": {"queue": door_access_queue},
            "update_member_to_groups": {"queue": batch_queue},
            "door_access_create_credential": {"queue": door_access_queue},
            "door_access_onboard_member": {"queue": door_access_queue},
        },
    )


def create_app() -> FastAPI:
    app = FastAPI(title="GMS Members API", version="1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    install_session_middleware(app)
    install_exception_handlers(app)
    _configure_celery()

    from members_service import members_api

    app.include_router(members_api)
    return app


app = create_app()

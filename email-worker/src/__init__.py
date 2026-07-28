from celery import Celery, Task
from flask import Flask
from kombu import Queue

from gmsshared.src.config import get_config
from gmsshared import db

def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with db.session_scope():
                return self.run(*args, **kwargs)

    celery_app = Celery(
        "email-worker",
        task_cls=FlaskTask,
        broker=get_config().BROKER_URI,
        backend=get_config().BACKEND_URI,
        include=[
            "email-worker.src.emails.session",
            "email-worker.src.emails.contact",
            "email-worker.src.emails.admin",
        ],
    )

    email_queue = f"'{get_config().ENV}-gms:emails'"

    celery_app.conf.update(
        task_serializer="json",
        result_serializer="json",
        enable_utc=True,
        broker_connection_retry_on_startup=True,
        task_queues=(Queue(email_queue),),
        task_routes=(
            [
                "owner_verification_email", {"queue": email_queue},
                "staff_account_verification_email", {"queue": email_queue},
                "staff_password_reset_email", {"queue": email_queue},
                "contact_app_download_link_email", {"queue": email_queue},
                "contact_app_verification_code_email", {"queue": email_queue},
                "contact_app_forgotten_password_code_email", {"queue": email_queue},
                "booking_cancellation_email", {"queue": email_queue},
                "updated_session_email", {"queue": email_queue},
                "create_single_session_pt_email", {"queue": email_queue},
                "create_recurring_session_pt_email", {"queue": email_queue},
                "updated_single_session_pt_email", {"queue": email_queue},
                "updated_recurring_session_pt_email", {"queue": email_queue},
                "session_cancellation_pt_coach_email", {"queue": email_queue},
                "session_cancellation_pt_member_email", {"queue": email_queue},
                "owner_onboard_admin_email", {"queue": email_queue},
                "add_to_waitlist_email", {"queue": email_queue},
                "promote_waitlist_to_registered_email", {"queue": email_queue},
                "profile_setup_email", {"queue": email_queue},
            ]
        ),
    )
    celery_app.set_default()
    return celery_app

def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())
    return celery_init_app(app)

worker_service = create_app()
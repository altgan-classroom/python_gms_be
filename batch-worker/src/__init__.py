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
        "batch-worker",
        task_cls=FlaskTask,
        broker=get_config().BROKER_URI,
        backend=get_config().BACKEND_URI,
        include=[
            "batch-worker.src.other.tasks.session",
        ],
    )

    batch_queue = f"'{get_config().ENV}-gms:batch-queue'"

    celery_app.conf.update(
        task_events=True,
        worker_send_task_events=True,
        worker_concurrency=1,
        task_serializer="json",
        result_serializer="json",
        enable_utc=True,
        log_level="DEBUG",
        broker_connection_retry_on_startup=True,
        task_queues=(Queue(batch_queue),),
        task_routes=(
            [
                "credit_noshows", {"queue": batch_queue},
            ]
        ),
    )
    celery_app.set_default()
    return celery_app


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())
    return celery_init_app(app)


scheduled_worker = create_app()

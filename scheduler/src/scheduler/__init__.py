from celery import Celery
from celery.schedules import crontab

from kombu import Queue
from gmsshared.src.config import get_config

scheduler_service = Celery(
    "scheduler",
    broker=get_config().BROKER_URI,
    backend=get_config().BACKEND_URI,
)

scheduler_service.conf.beat_schedule = {
    "credit_noshows_at_morning": {"task": "credit_noshows", "schedule": crontab(hour="11", minute="00")},
    "credit_noshows_at_evening": {"task": "credit_noshows", "schedule": crontab(hour="18", minute="30")},
}

batch_queue = f"'{get_config().ENV}-gms:batch-queue'"
scheduler_service.conf.update(
    task_events=True,
    worker_send_task_events=True,
    task_serializer="json",
    result_serializer="json",
    enable_utc=True,
    log_level="DEBUG",
    broker_connection_retry_on_startup=True,
    beat_max_loop_interval=17,
    task_queues=(Queue(batch_queue),),
    task_routes={
        "credit_noshows": batch_queue,
    },
)

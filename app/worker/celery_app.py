from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "autocheck_worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.worker.tasks"],
)

celery_app.conf.update(
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

from celery import Celery
from ..config.config import config

celery_app = Celery(
    "auto_heal_worker",
    broker=config.REDIS_URL,
    backend=config.REDIS_URL,
    include=["apps.backend.src.infrastructure.celery.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

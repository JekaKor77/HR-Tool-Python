from celery import Celery
from app_config import settings

celery = Celery(
    "hr_tool",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery.conf.update({
    'task_serializer': 'json',
    'accept_content': ['json'],
    'result_serializer': 'json',
    'timezone': 'UTC',
    'enable_utc': True,
    'task_acks_late': True,
    'worker_prefetch_multiplier': 1,
    'imports': ('celery_app.tasks',)
})

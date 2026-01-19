from celery.app import Celery

from src.settings import settings

celery_app = Celery(__name__, broker=settings.redis_url, backend=settings.redis_url)
celery_app.autodiscover_tasks(["src.tasks"])

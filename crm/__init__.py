# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

__all__ = ('celery_app',)

# This ensures that the Celery app is loaded when Django starts
# and allows the @shared_task decorator to work properly

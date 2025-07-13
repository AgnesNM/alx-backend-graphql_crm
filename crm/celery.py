import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')

# Create the Celery app
app = Celery('crm')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs
app.autodiscover_tasks()

# Configure Celery to use Redis as the broker
app.conf.update(
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0',
    timezone='UTC',
    enable_utc=True,
)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

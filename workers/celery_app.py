from celery import Celery

app = Celery(
    'shikigami',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
    include=['workers.tasks']
)

app.conf.update(
    timezone='UTC',
    enable_utc=True,
    worker_concurrency=4
)
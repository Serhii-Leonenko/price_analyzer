import os

from celery import Celery, group, signature
from celery.signals import worker_ready

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

app = Celery("price_analyzer")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@worker_ready.connect
def on_worker_ready(sender, **kwargs):
    job = group(
        signature("currencies.tasks.sync_exchange_rates_for_date"),
        signature("products.tasks.import_all_products"),
        signature("prices.tasks.sync_all_store_prices"),
    )
    job.apply_async()

from celery import shared_task, signature


@shared_task
def sync_all_store_prices():
    from prices.services import PriceSyncService

    result = PriceSyncService().execute()

    signature("alerts.tasks.check_price_alerts").apply_async()

    return result

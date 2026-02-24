from celery import shared_task


@shared_task
def sync_today_exchange_rates():
    from currencies.services import ExchangeRateSyncService

    return ExchangeRateSyncService().execute()


@shared_task
def sync_exchange_rates_for_date(date):
    from currencies.services import ExchangeRateSyncService

    return ExchangeRateSyncService().execute(for_date=date)

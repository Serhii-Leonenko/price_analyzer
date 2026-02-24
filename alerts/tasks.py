from celery import shared_task


@shared_task
def check_price_alerts():
    from alerts.services import PriceAlertService

    return PriceAlertService().check_and_send()

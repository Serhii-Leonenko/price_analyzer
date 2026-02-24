from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone

from alerts.interfaces import INotificationService, IPriceAlertService
from alerts.models import PriceAlert
from currencies.interfaces import ICurrencyConversionService
from currencies.services import CurrencyConversionService
from prices.interfaces import IPriceQueryService
from prices.services import PriceQueryService


User = get_user_model()


class EmailNotificationService(INotificationService):
    def send_price_alert(
        self,
        product_name: str,
        email: str,
        target_price: Decimal,
        current_min_price: Decimal,
    ) -> None:
        send_mail(
            subject=f"Price alert: {product_name}",
            message=(
                f"Hello!\n\n"
                f"The price for '{product_name}' has dropped to {current_min_price}.\n"
                f"Your target price was {target_price}.\n\n"
                f"Check it out now!"
            ),
            recipient_list=[email],
            fail_silently=True,
        )


class PriceAlertService(IPriceAlertService):
    def __init__(
        self,
        price_query: IPriceQueryService | None = None,
        notification: INotificationService | None = None,
        conversion: ICurrencyConversionService | None = None,
    ):
        self._price_query = price_query or PriceQueryService()
        self._notification = notification or EmailNotificationService()
        self._conversion = conversion or CurrencyConversionService()

    def create(
        self,
        user: User,
        product_id: int,
        target_price_cents: int,
        currency_code: str
    ) -> PriceAlert:
        alert, _ = PriceAlert.objects.update_or_create(
            user=user,
            product_id=product_id,
            defaults={
                "target_price_cents": target_price_cents,
                "currency_code": currency_code,
                "is_active": True,
                "triggered_at": None,
            },
        )
        return alert

    def check_and_send(self) -> int:
        active_alerts = PriceAlert.objects.filter(is_active=True).select_related(
            "user", "product"
        )
        sent = 0

        for alert in active_alerts:
            price_range = self._price_query.get_price_range_today(alert.product_id)
            min_price_cents = price_range.min_price_cents

            if min_price_cents is None:
                continue

            if min_price_cents <= alert.target_price_cents:
                min_price_converted = self._conversion.convert(
                    min_price_cents, alert.currency_code
                )
                target_price_converted = self._conversion.convert(
                    alert.target_price_cents, alert.currency_code
                )
                self._notification.send_price_alert(
                    product_name=alert.product.name,
                    email=alert.user.email,
                    target_price=target_price_converted,
                    current_min_price=min_price_converted,
                )
                alert.is_active = False
                alert.triggered_at = timezone.now()
                alert.save(update_fields=["is_active", "triggered_at"])
                sent += 1

        return sent

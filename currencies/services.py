from datetime import date
from decimal import Decimal

import httpx
from django.conf import settings
from django.utils import timezone

from currencies.interfaces import ICurrencyConversionService, IExchangeRateSyncService
from currencies.models import Currency, ExchangeRate
from prices.utils import cents_to_usd


class ExchangeRateSyncService(IExchangeRateSyncService):
    def _fetch_nbu_rates(self, for_date: date) -> list[dict]:
        params = {"json": "", "date": for_date.strftime("%Y%m%d")}

        with httpx.Client(timeout=10) as client:
            response = client.get(settings.EXCHANGE_RATE_API_URL, params=params)
            response.raise_for_status()

            return response.json()

    def execute(self, for_date: date | None = None) -> int:
        target_date = for_date or date.today()
        raw_rates = self._fetch_nbu_rates(target_date)

        usd_rate = [r for r in raw_rates if r["cc"] == "USD"][0]
        if not usd_rate:
            return 0

        usd_to_uah = Decimal(str(usd_rate["rate"]))
        count = 0

        for item in raw_rates:
            currency, _ = Currency.objects.get_or_create(
                code=item["cc"],
                defaults={"name": item["txt"]},
            )
            rate_uah = Decimal(str(item["rate"])) / Decimal(str(item.get("units", 1)))
            ExchangeRate.objects.update_or_create(
                currency=currency,
                date=target_date,
                defaults={"rate_to_usd": rate_uah / usd_to_uah},
            )
            count += 1

        return count


class CurrencyConversionService(ICurrencyConversionService):
    def convert(
        self, amount_cents: int, currency_code: str, for_date: date | None = None
    ) -> Decimal | None:
        amount_usd = cents_to_usd(amount_cents)

        if currency_code.upper() == "USD":
            return amount_usd

        target_date = for_date or timezone.now().date()

        rate = ExchangeRate.objects.filter(
            currency__code=currency_code.upper(), date__lte=target_date
        ).latest("date")

        if not rate:
            return None

        return round(amount_usd / rate.rate_to_usd, 2)

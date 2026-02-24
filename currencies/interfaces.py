from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal


class IExchangeRateSyncService(ABC):
    @abstractmethod
    def execute(self, for_date: date | None = None) -> int:
        pass


class ICurrencyConversionService(ABC):
    @abstractmethod
    def convert(
        self, amount_usd_cents: int, currency_code: str, for_date: date | None = None
    ) -> Decimal | None:
        pass

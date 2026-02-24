from abc import ABC, abstractmethod
from decimal import Decimal

from prices.choices import TrendChoices
from prices.dtos import (
    PriceRangeDTO,
    ProductPriceDTO,
    StorePriceDTO,
    StorePriceHistoryDTO,
)


class IStorePriceFetcher(ABC):
    @abstractmethod
    def fetch(self) -> list[ProductPriceDTO]:
        pass


class IPriceSyncService(ABC):
    @abstractmethod
    def execute(self) -> int:
        pass


class IPriceQueryService(ABC):
    @abstractmethod
    def get_today_prices(self, product_id: int) -> list[StorePriceDTO]:
        pass

    @abstractmethod
    def get_price_range_today(self, product_id: int) -> PriceRangeDTO:
        pass

    @abstractmethod
    def get_average_last_30_days(self, product_id: int) -> Decimal | None:
        pass

    @abstractmethod
    def get_trend(self, product_id: int) -> TrendChoices:
        pass

    @abstractmethod
    def get_history(self, product_id: int) -> list[StorePriceHistoryDTO]:
        pass

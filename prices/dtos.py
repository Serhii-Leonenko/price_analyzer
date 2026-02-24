import datetime
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ProductPriceDTO:
    external_id: int
    price: Decimal


@dataclass(frozen=True)
class StorePriceDTO:
    store_name: str
    store_slug: str
    price_cents: int


@dataclass(frozen=True)
class PriceRangeDTO:
    min_price_cents: int | None
    max_price_cents: int | None


@dataclass(frozen=True)
class StorePriceHistoryDTO:
    store_name: str
    store_slug: str
    price_cents: int
    created_at: datetime.datetime

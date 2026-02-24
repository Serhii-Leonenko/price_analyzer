import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import timedelta
from decimal import Decimal

import httpx
from django.conf import settings
from django.db import models
from django.db.models import Avg
from django.utils import timezone as django_timezone

from prices.choices import TrendChoices
from prices.dtos import (
    PriceRangeDTO,
    ProductPriceDTO,
    StorePriceDTO,
    StorePriceHistoryDTO,
)
from prices.interfaces import IPriceQueryService, IPriceSyncService, IStorePriceFetcher
from prices.models import PriceSnapshot
from prices.utils import usd_to_cents
from products.models import ProductStore, Store

logger = logging.getLogger(__name__)


class DummyJsonPriceFetcher(IStorePriceFetcher):
    TIMEOUT = 10

    def fetch(self) -> list[ProductPriceDTO]:
        with httpx.Client(timeout=self.TIMEOUT) as client:
            response = client.get(settings.STORE_APIS["dummyjson"], params={"limit": 0})
            response.raise_for_status()
            data = response.json()

        return [
            ProductPriceDTO(
                external_id=int(item["id"]),
                price=Decimal(str(item["price"])),
            )
            for item in data.get("products", [])
        ]


class FakeStorePriceFetcher(IStorePriceFetcher):
    TIMEOUT = 10

    def fetch(self) -> list[ProductPriceDTO]:
        with httpx.Client(timeout=self.TIMEOUT) as client:
            response = client.get(settings.STORE_APIS["fakestore"])
            response.raise_for_status()
            data = response.json()

        return [
            ProductPriceDTO(
                external_id=int(item["id"]),
                price=Decimal(str(item["price"])),
            )
            for item in data
        ]


_PRICE_FETCHERS: dict[str, IStorePriceFetcher] = {
    "dummyjson": DummyJsonPriceFetcher(),
    "fakestore": FakeStorePriceFetcher(),
}


class PriceSyncService(IPriceSyncService):
    CONCURRENCY = 10

    def __init__(self, fetchers: dict[str, IStorePriceFetcher] | None = None):
        self._fetchers = fetchers or _PRICE_FETCHERS

    def _fetch_for_store(
        self,
        store: Store,
    ) -> tuple[Store, list[ProductPriceDTO]]:
        fetcher = self._fetchers.get(store.slug)

        if not fetcher:
            return store, []

        items = fetcher.fetch()

        return store, items

    def execute(self) -> int:
        stores = Store.objects.all()

        total = 0
        with ThreadPoolExecutor(max_workers=self.CONCURRENCY) as executor:
            future_to_store = {
                executor.submit(self._fetch_for_store, store): store for store in stores
            }

            for future in as_completed(future_to_store):
                store, items = future.result()

                try:
                    total += self._add_snapshots(store, items)
                except Exception:
                    logger.exception(f"Failed to persist prices for store {store.slug}")
                    continue

        return total

    def _add_snapshots(
        self, store: Store, product_prices: list[ProductPriceDTO]
    ) -> int:
        external_ids = {item.external_id for item in product_prices}
        product_stores = ProductStore.objects.filter(
            store=store, external_id__in=external_ids
        )
        product_store_map = {item.external_id: item for item in product_stores}

        snapshots = [
            PriceSnapshot(
                product_store=product_store_map[item.external_id],
                price_cents=usd_to_cents(item.price),
            )
            for item in product_prices
            if item.external_id in product_store_map
        ]
        PriceSnapshot.objects.bulk_create(
            snapshots, batch_size=1000, ignore_conflicts=True
        )

        return len(snapshots)


class PriceQueryService(IPriceQueryService):
    def get_today_prices(self, product_id: int) -> list[StorePriceDTO]:
        today_start = django_timezone.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        snapshots = (
            PriceSnapshot.objects.filter(
                product_store__product_id=product_id, created_at__gte=today_start
            )
            .select_related("product_store__store")
            .order_by("product_store__store__slug", "-created_at")
            .distinct("product_store__store__slug")
        )

        return [
            StorePriceDTO(
                store_name=snapshot.product_store.store.name,
                store_slug=snapshot.product_store.store.slug,
                price_cents=snapshot.price_cents,
            )
            for snapshot in snapshots
        ]

    def get_price_range_today(self, product_id: int) -> PriceRangeDTO:
        prices = self.get_today_prices(product_id)

        if not prices:
            return PriceRangeDTO(min_price_cents=None, max_price_cents=None)

        values = [price.price_cents for price in prices]

        return PriceRangeDTO(min_price_cents=min(values), max_price_cents=max(values))

    def get_average_last_30_days(self, product_id: int) -> int | None:
        cutoff = django_timezone.now() - timedelta(days=30)

        avg_price = PriceSnapshot.objects.filter(
            product_store__product_id=product_id,
            created_at__gte=cutoff,
        ).aggregate(avg_price=Avg("price_cents", output_field=models.IntegerField()))[
            "avg_price"
        ]

        return avg_price

    def get_trend(self, product_id: int) -> TrendChoices:
        price_range = self.get_price_range_today(product_id)
        avg_30 = self.get_average_last_30_days(product_id)

        if not avg_30 or price_range.min_price_cents is None:
            return TrendChoices.UNKNOWN

        today_avg = (price_range.min_price_cents + price_range.max_price_cents) / 2

        if today_avg > avg_30:
            return TrendChoices.UP

        if today_avg < avg_30:
            return TrendChoices.DOWN

        return TrendChoices.STABLE

    def get_history(self, product_id: int) -> list[StorePriceHistoryDTO]:
        snapshots = (
            PriceSnapshot.objects.filter(product_store__product_id=product_id)
            .select_related("product_store__store")
            .order_by("created_at")
        )

        return [
            StorePriceHistoryDTO(
                store_name=snapshot.product_store.store.name,
                store_slug=snapshot.product_store.store.slug,
                price_cents=snapshot.price_cents,
                created_at=snapshot.created_at,
            )
            for snapshot in snapshots
        ]

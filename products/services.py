import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

import httpx
from django.conf import settings
from django.db import transaction
from django.db.models import Q

from products.dtos import ProductDTO
from products.errors import FetcherNotFoundError
from products.interfaces import IProductImporter, IStoreFetcher
from products.models import Product, ProductStore, Store

logger = logging.getLogger(__name__)


class DummyJsonProductFetcher(IStoreFetcher):
    TIMEOUT = 10

    def fetch(self) -> list[ProductDTO]:
        with httpx.Client(timeout=self.TIMEOUT) as client:
            response = client.get(settings.STORE_APIS["dummyjson"], params={"limit": 0})
            response.raise_for_status()
            data = response.json()

        return [
            ProductDTO(
                id=item["id"],
                name=item["title"],
                description=item.get("description", ""),
            )
            for item in data.get("products", [])
        ]


class FakeStoreProductFetcher(IStoreFetcher):
    TIMEOUT = 10

    def fetch(self) -> list[ProductDTO]:
        with httpx.Client(timeout=self.TIMEOUT) as client:
            response = client.get(settings.STORE_APIS["fakestore"])
            response.raise_for_status()

            data = response.json()

        return [
            ProductDTO(
                id=item["id"],
                name=item["title"],
                description=item.get("description", ""),
            )
            for item in data
        ]


_PRODUCT_FETCHERS: dict[str, IStoreFetcher] = {
    "dummyjson": DummyJsonProductFetcher(),
    "fakestore": FakeStoreProductFetcher(),
}


class ProductImportService(IProductImporter):
    CONCURRENCY = 10

    def __init__(self, fetchers: dict[str, IStoreFetcher] | None = None):
        self._fetchers = fetchers or _PRODUCT_FETCHERS

    def _fetch_for_store(self, store: Store) -> tuple[Store, list[ProductDTO]]:
        fetcher = self._fetchers.get(store.slug)

        if not fetcher:
            raise FetcherNotFoundError(f"Fetcher for {store.slug} is not implemented")

        items = fetcher.fetch()

        return store, items

    def execute(self) -> int:
        stores = Store.objects.all().only("id", "slug")

        products_created = 0

        with ThreadPoolExecutor(max_workers=self.CONCURRENCY) as executor:
            future_to_store = {
                executor.submit(self._fetch_for_store, store): store for store in stores
            }

            for future in as_completed(future_to_store):
                store = future_to_store[future]
                try:
                    store_id, products = future.result()
                except httpx.HTTPError:
                    logger.exception(f"Failed to fetch store {store.slug}")

                    continue

                try:
                    products_created += self._store_products(store, products)
                except Exception:
                    logger.exception(
                        f"Failed to persist products for store {store.slug}"
                    )
                    continue

        return products_created

    def _store_products(self, store: Store, products: list[ProductDTO]) -> int:
        if not products:
            return 0

        products_by_name = {product.name.strip(): product for product in products}
        names = set(products_by_name.keys())

        if not products_by_name:
            return 0

        existing_names = set(
            Product.objects.filter(name__in=names).values_list("name", flat=True)
        )

        to_create = [
            Product(name=name, description=products_by_name[name].description)
            for name in names
            if name not in existing_names
        ]

        with transaction.atomic():
            if to_create:
                Product.objects.bulk_create(
                    to_create,
                    ignore_conflicts=True,
                    batch_size=1000,
                )

            products_without_store = Product.objects.filter(
                ~Q(stores=store),
                name__in=names,
            ).values_list(
                "id",
                "name",
            )

            added_stores = ProductStore.objects.bulk_create(
                [
                    ProductStore(
                        product_id=product_id,
                        store=store,
                        external_id=products_by_name[product_name].id,
                    )
                    for product_id, product_name in products_without_store
                ],
                ignore_conflicts=True,
                batch_size=1000,
            )

        return len(added_stores)

from collections import defaultdict
from decimal import Decimal

from drf_extra.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.request import Request
from rest_framework.response import Response

from currencies.interfaces import ICurrencyConversionService
from currencies.services import CurrencyConversionService
from prices.choices import TrendChoices
from prices.interfaces import IPriceQueryService
from prices.services import PriceQueryService
from products.models import Product
from products.serializers import (
    PriceHistorySerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    StorePriceSerializer,
)


class ProductViewSet(GenericViewSet):
    queryset = Product.objects.all().order_by("name")

    response_action_serializer_classes = {
        "list": ProductListSerializer,
        "retrieve": ProductDetailSerializer,
        "all_prices": StorePriceSerializer,
        "price_history": PriceHistorySerializer,
    }

    filter_backends = [SearchFilter]
    search_fields = ["name"]

    def __init__(
        self,
        price_query: IPriceQueryService | None = None,
        conversion: ICurrencyConversionService | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._price_query: IPriceQueryService = price_query or PriceQueryService()
        self._conversion: ICurrencyConversionService = (
            conversion or CurrencyConversionService()
        )

    def _get_currency(self, request: Request) -> str:
        return request.query_params.get("currency", "USD").upper()

    def _get_ordering(self, request: Request) -> str:
        return request.query_params.get("ordering", "price").lower()

    def _convert(self, amount: int | None, currency: str) -> Decimal | None:
        if amount is None:
            return None

        return self._conversion.convert(amount, currency)

    def list(self, request: Request, *args, **kwargs) -> Response:
        queryset = self.filter_queryset(self.get_queryset())

        currency_filter = self._get_currency(request)
        ordering_filter = self._get_ordering(request)

        products_data = []
        for product in queryset:
            price_range = self._price_query.get_price_range_today(product.id)
            trend = self._price_query.get_trend(product.id)

            price_min = self._convert(price_range.min_price_cents, currency_filter)
            price_max = self._convert(price_range.max_price_cents, currency_filter)

            products_data.append(
                {
                    "id": product.id,
                    "name": product.name,
                    "price_min": price_min,
                    "price_max": price_max,
                    "trend": trend,
                    "currency": currency_filter,
                }
            )

        if ordering_filter in ("price", "-price"):
            reverse = ordering_filter.startswith("-")
            products_data.sort(
                key=lambda x: x["price_min"] or Decimal(0), reverse=reverse
            )
        elif ordering_filter in ("trend", "-trend"):
            trend_order = {
                TrendChoices.UP: 0,
                TrendChoices.STABLE: 1,
                TrendChoices.DOWN: 2,
                TrendChoices.UNKNOWN: 3,
            }

            reverse = ordering_filter.startswith("-")
            products_data.sort(
                key=lambda x: trend_order.get(x["trend"], 3), reverse=reverse
            )

        serializer = self.get_response_serializer(products_data, many=True)

        return Response(serializer.data)

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        product = self.get_object()
        currency = self._get_currency(request)
        price_range = self._price_query.get_price_range_today(product.id)

        data = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price_min": self._convert(price_range.min_price_cents, currency),
            "price_max": self._convert(price_range.max_price_cents, currency),
            "currency": currency,
        }

        serializer = self.get_response_serializer(data)

        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="all-prices")
    def all_prices(self, request: Request, pk=None) -> Response:
        product = self.get_object()
        currency = self._get_currency(request)
        store_prices = self._price_query.get_today_prices(product.id)

        store_prices = [
            {
                "store": price.store_name,
                "store_slug": price.store_slug,
                "price": self._convert(price.price_cents, currency),
            }
            for price in store_prices
        ]

        serializer = self.get_response_serializer(store_prices, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="price-history")
    def price_history(self, request: Request, pk=None) -> Response:
        product = self.get_object()
        currency = self._get_currency(request)
        history_prices = self._price_query.get_history(product.id)

        history = [
            {
                "store": price.store_name,
                "store_slug": price.store_slug,
                "price": self._convert(price.price_cents, currency),
                "created_at": price.created_at,
            }
            for price in history_prices
        ]

        by_date = defaultdict(list)
        for price in history_prices:
            day = price.created_at.date()
            converted = self._convert(price.price_cents, currency)

            if converted is not None:
                by_date[day].append(converted)

        average_history = [
            {
                "price": sum(prices) / len(prices),
                "date": day,
            }
            for day, prices in sorted(by_date.items())
        ]

        serializer = self.get_response_serializer(
            {"history": history, "average_history": average_history}
        )

        return Response(serializer.data)

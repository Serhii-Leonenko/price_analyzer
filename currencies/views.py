from drf_extra.mixins import ListModelMixin
from drf_extra.viewsets import GenericViewSet

from .models import Currency, ExchangeRate
from .serializers import CurrencySerializer, ExchangeRateSerializer


class CurrencyViewSet(ListModelMixin, GenericViewSet):
    queryset = Currency.objects.all().order_by("code")

    response_action_serializer_classes = {
        "list": CurrencySerializer,
    }


class ExchangeRateViewSet(ListModelMixin, GenericViewSet):
    queryset = ExchangeRate.objects.select_related("currency").order_by(
        "-date", "currency__code"
    )

    response_action_serializer_classes = {
        "list": ExchangeRateSerializer,
    }

    filterset_fields = ["currency__code", "date"]

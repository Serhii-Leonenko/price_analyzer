from drf_extra.mixins import CreateModelMixin
from drf_extra.viewsets import GenericViewSet

from alerts.interfaces import IPriceAlertService
from alerts.models import PriceAlert
from alerts.serializers import PriceAlertCreateSerializer, PriceAlertResponseSerializer
from alerts.services import PriceAlertService


class PriceAlertViewSet(
    CreateModelMixin,
    GenericViewSet
):
    """
    Endpoints for managing price alerts.
    """
    request_action_serializer_classes = {
        "create": PriceAlertCreateSerializer,
    }

    response_action_serializer_classes = {
        "create": PriceAlertResponseSerializer,
    }

    def __init__(self, service: IPriceAlertService | None = None, **kwargs):
        super().__init__(**kwargs)

        self._service: IPriceAlertService = service or PriceAlertService()

    def get_queryset(self):
        return PriceAlert.objects.filter(
            user=self.request.user
        ).select_related(
            "product"
        )

    def perform_create(self, serializer: PriceAlertCreateSerializer) -> PriceAlert:
        return self._service.create(
            user=self.request.user,
            product_id=serializer.validated_data["product_id"],
            target_price_cents=serializer.validated_data["target_price_cents"],
            currency_code=serializer.validated_data["currency_code"],
        )

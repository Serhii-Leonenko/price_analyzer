from abc import ABC, abstractmethod
from decimal import Decimal

from django.contrib.auth import get_user_model

from alerts.models import PriceAlert

User = get_user_model()


class INotificationService(ABC):
    @abstractmethod
    def send_price_alert(
        self,
        product_name: str,
        email: str,
        target_price: Decimal,
        current_min_price: Decimal,
    ) -> None:
        pass


class IPriceAlertService(ABC):
    @abstractmethod
    def create(
        self,
        user: User,
        product_id: int,
        target_price_cents: int,
        currency_code: str
    ) -> PriceAlert:
        pass

    @abstractmethod
    def check_and_send(self) -> int:
        pass

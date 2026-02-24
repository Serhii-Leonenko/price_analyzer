from abc import ABC, abstractmethod
from decimal import Decimal

from alerts.models import PriceAlert


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
    def create(self, user, product_id: int, target_price_usd: Decimal) -> PriceAlert:
        pass

    @abstractmethod
    def delete(self, user, product_id: int) -> None:
        pass

    @abstractmethod
    def check_and_send(self) -> int:
        pass

from django.conf import settings
from django.db import models

from base.models import BaseTimestampedModel
from products.models import Product


class PriceAlert(BaseTimestampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="price_alerts",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="price_alerts",
    )
    target_price_cents = models.IntegerField()
    is_active = models.BooleanField(default=True)
    triggered_at = models.DateTimeField(null=True, blank=True)
    currency_code = models.CharField(max_length=10)

    class Meta:
        db_table = "price_alerts"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"], name="unique_user_product"
            ),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.product.name} - {self.target_price_cents}"

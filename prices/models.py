from django.db import models

from base.models import BaseTimestampedModel
from products.models import ProductStore


class PriceSnapshot(BaseTimestampedModel):
    product_store = models.ForeignKey(
        ProductStore,
        on_delete=models.CASCADE,
        related_name="price_snapshots",
    )
    price_cents = models.PositiveIntegerField()

    class Meta:
        db_table = "price_snapshots"
        indexes = [
            models.Index(fields=["product_store", "created_at"]),
        ]

    def __str__(self):
        return f"{self.product_store} - {self.price_cents}"

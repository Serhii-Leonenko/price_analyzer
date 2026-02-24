from django.db import models

from base.models import BaseTimestampedModel
from products.choices import StoreChoices


class Store(BaseTimestampedModel):
    slug = models.CharField(max_length=50, unique=True, choices=StoreChoices.choices)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "stores"

    def __str__(self):
        return self.name


class Product(BaseTimestampedModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    stores = models.ManyToManyField(
        Store, through="ProductStore", related_name="products"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "products"
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name


class ProductStore(BaseTimestampedModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_stores"
    )
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="product_stores"
    )
    external_id = models.BigIntegerField()

    class Meta:
        db_table = "product_stores"

        constraints = [
            models.UniqueConstraint(
                fields=["product", "store"], name="uniq_product_store"
            )
        ]

        indexes = [
            models.Index(fields=["store", "external_id"]),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.store.name}"

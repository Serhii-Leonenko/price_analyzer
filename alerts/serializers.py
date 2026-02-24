from rest_framework import serializers

from alerts.models import PriceAlert


class PriceAlertCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    target_price = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency = serializers.CharField()


class PriceAlertResponseSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = PriceAlert
        fields = (
            "id",
            "product_id",
            "product_name",
            "target_price_usd",
            "is_active",
            "created_at",
            "triggered_at",
        )

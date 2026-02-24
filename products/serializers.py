from rest_framework import serializers

from prices.choices import TrendChoices


class StorePriceSerializer(serializers.Serializer):
    store = serializers.CharField()
    store_slug = serializers.CharField()
    price = serializers.DecimalField(max_digits=12, decimal_places=2)


class ProductListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    price_min = serializers.DecimalField(
        max_digits=12, decimal_places=2, allow_null=True
    )
    price_max = serializers.DecimalField(
        max_digits=12, decimal_places=2, allow_null=True
    )
    trend = serializers.ChoiceField(choices=TrendChoices.choices)
    currency = serializers.CharField()


class ProductDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    price_min = serializers.DecimalField(
        max_digits=12, decimal_places=2, allow_null=True, read_only=True
    )
    price_max = serializers.DecimalField(
        max_digits=12, decimal_places=2, allow_null=True, read_only=True
    )
    currency = serializers.CharField(read_only=True)


class PriceHistoryStoreSerializer(serializers.Serializer):
    store = serializers.CharField()
    store_slug = serializers.CharField()
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    created_at = serializers.DateTimeField()


class PriceAverageHistorySerializer(serializers.Serializer):
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    date = serializers.DateField()


class PriceHistorySerializer(serializers.Serializer):
    history = PriceHistoryStoreSerializer(many=True)
    average_history = PriceAverageHistorySerializer(many=True)

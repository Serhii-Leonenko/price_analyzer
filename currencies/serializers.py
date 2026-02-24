from rest_framework import serializers

from currencies.models import Currency, ExchangeRate


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ("code", "name")


class ExchangeRateSerializer(serializers.ModelSerializer):
    currency_code = serializers.CharField(source="currency.code", read_only=True)
    currency_name = serializers.CharField(source="currency.name", read_only=True)

    class Meta:
        model = ExchangeRate
        fields = ("currency_code", "currency_name", "rate_to_usd", "date")

from django.db import models


class Currency(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "currencies"
        verbose_name_plural = "currencies"

    def __str__(self):
        return self.code


class ExchangeRate(models.Model):
    currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name="exchange_rates"
    )
    rate_to_usd = models.DecimalField(max_digits=18, decimal_places=6)
    date = models.DateField(db_index=True)

    class Meta:
        db_table = "exchange_rates"
        constraints = [
            models.UniqueConstraint(
                fields=["currency", "date"], name="unique_currency_date"
            ),
        ]

    def __str__(self):
        return f"{self.currency.code} - {self.rate_to_usd} - {self.date}"

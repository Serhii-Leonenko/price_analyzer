from django.contrib import admin

from alerts.models import PriceAlert


@admin.register(PriceAlert)
class PriceAlertAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "product",
        "target_price_cents",
        "is_active",
        "created_at",
        "triggered_at",
    )
    list_filter = ("is_active",)

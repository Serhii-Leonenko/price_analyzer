from django.contrib import admin

from prices.models import PriceSnapshot


@admin.register(PriceSnapshot)
class PriceSnapshotAdmin(admin.ModelAdmin):
    list_display = ("product_store", "price_cents", "created_at")
    list_filter = ("product_store__store",)
    ordering = ("-created_at",)

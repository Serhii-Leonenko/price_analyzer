from django.contrib import admin

from products.models import Product, ProductStore, Store


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("slug", "name")


class ProductStoreInline(admin.TabularInline):
    model = ProductStore
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)
    inlines = [ProductStoreInline]

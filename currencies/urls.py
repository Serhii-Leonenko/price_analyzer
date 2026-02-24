from rest_framework.routers import DefaultRouter

from currencies.views import CurrencyViewSet, ExchangeRateViewSet

app_name = "currencies"

router = DefaultRouter()
router.register("currencies", CurrencyViewSet, basename="currency")
router.register("exchange-rates", ExchangeRateViewSet, basename="exchange-rate")

urlpatterns = router.urls

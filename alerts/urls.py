from rest_framework.routers import DefaultRouter

from alerts.views import PriceAlertViewSet

app_name = "alerts"

router = DefaultRouter()
router.register("alerts", PriceAlertViewSet, basename="alert")

urlpatterns = router.urls

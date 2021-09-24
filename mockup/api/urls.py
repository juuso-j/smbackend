from django.urls import path, include
from rest_framework import routers
from . import views

app_name = "mockup"

router = routers.DefaultRouter()

router.register("units", views.UnitViewSet, basename="units")
router.register("geometries", views.GeometryViewSet, basename="geometries")
router.register("chargingstations", views.ChargingStationContentViewSet, basename="chargingstations")
router.register("gasfillingstations", views.GasFillingStationtContentViewSet, basename="gasfillingstations")
urlpatterns = [
    path("", include(router.urls), name="eco-counter"),
]
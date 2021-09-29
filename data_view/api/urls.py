from django.urls import path, include
from rest_framework import routers
from . import views

app_name = "mockup"

router = routers.DefaultRouter()
router.register("content_types", views.ContentTypesViewSet, basename="content_types")
router.register("units", views.UnitViewSet, basename="units")
router.register("geometries", views.GeometryViewSet, basename="geometries")
router.register("charging_stations", views.ChargingStationContentViewSet, basename="charging_stations")
router.register("gas_filling_stations", views.GasFillingStationtContentViewSet, basename="gas_filling_stations")
urlpatterns = [
    path("", include(router.urls), name="eco-counter"),
]
from django.urls import path, include
from rest_framework import routers
from . import views

app_name = "data_view"

router = routers.DefaultRouter()
router.register("group_types", views.GroupTypesViewSet, basename="group_types")
router.register("content_types", views.ContentTypesViewSet, basename="content_types")

router.register("mobile_units", views.MobileUnitViewSet, basename="mobile_units")
router.register("mobile_unit_groups", views.MobileUnitGroupViewSet, basename="mobile_unit_groups")

#router.register("geometries", views.GeometryViewSet, basename="geometries")
router.register("charging_stations", views.ChargingStationContentViewSet, basename="charging_stations")
router.register("gas_filling_stations", views.GasFillingStationtContentViewSet, basename="gas_filling_stations")
urlpatterns = [
    path("", include(router.urls), name="eco-counter"),
]
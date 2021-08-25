from django.urls import path, include
from rest_framework import routers
from . import views

app_name = "eco_counter"

router = routers.SimpleRouter()
router.register("days", views.DayViewSet, basename="day")
router.register("locations", views.LocationViewSet, basename="location")

urlpatterns = [
    path("", include(router.urls)),
]
from django.urls import path, include
from rest_framework import routers
from . import views

app_name = "eco_counter"

router = routers.SimpleRouter()
router.register("days", views.DayViewSet, basename="day")
router.register("locations", views.LocationViewSet, basename="location")
router.register("week", views.WeekViewSet, basename="week")
router.register("week_day", views.WeekDayViewSet, basename="week_day")
router.register("week_data", views.WeekDataViewSet, basename="week_data")

urlpatterns = [
    path("", include(router.urls)),
]
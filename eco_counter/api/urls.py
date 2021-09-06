from django.urls import path, include
from rest_framework import routers
from . import views

app_name = "eco_counter"

router = routers.SimpleRouter()
router.register("stations", views.StationViewSet, basename="station")
router.register("hour-data", views.HourDataViewSet, basename="hour-data")
router.register("day-data", views.HourDataViewSet, basename="day-data")
router.register("week-data", views.WeekDataViewSet, basename="week-data")
router.register("month-data", views.MonthDataViewSet, basename="month-data")

router.register("weeks", views.WeekViewSet, basename="week")
router.register("days", views.DayViewSet, basename="days")
router.register("months", views.MonthViewSet, basename="month")

urlpatterns = [
    path("", include(router.urls)),
]
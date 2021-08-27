from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.response import Response
from .models import Day, Location, WeekData, WeekDay, Week, Month, MonthData
from .serializers import (
    DaySerializer,
    LocationSerializer,
    MonthDataSerializer,
    MonthSerializer,
    WeekDataSerializer,
    WeekDaySerializer, 
    WeekSerializer,
    WeekDataSerializer,
)


class DayViewSet(viewsets.ModelViewSet):
    queryset = Day.objects.all().order_by("date")
    serializer_class = DaySerializer
    #endpoint could be, get_day(loc_id, date)


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class WeekDayViewSet(viewsets.ModelViewSet):
    queryset = WeekDay.objects.all().order_by("date")
    serializer_class = WeekDaySerializer
    #get_weekday (loc_id, date)


class WeekViewSet(viewsets.ModelViewSet):
    queryset = Week.objects.all().order_by("week_number")
    serializer_class = WeekSerializer
    

class WeekDataViewSet(viewsets.ModelViewSet):
    queryset = WeekData.objects.all().order_by("id")
    serializer_class = WeekDataSerializer


class MonthViewSet(viewsets.ModelViewSet):
    queryset = Month.objects.all()
    serializer_class = MonthSerializer


class MonthDataViewSet(viewsets.ModelViewSet):
    queryset = MonthData.objects.all()
    serializer_class = MonthDataSerializer


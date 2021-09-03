from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.response import Response
from .models import Station, HourData, WeekData, Day, Week, Month, MonthData
from .serializers import (
    HourDataSerializer,
    StationSerializer,
    MonthDataSerializer,
    MonthSerializer,
    WeekDataSerializer,
    DaySerializer, 
    WeekSerializer,
    WeekDataSerializer,
)


class HourDataViewSet(viewsets.ModelViewSet):
    queryset = HourData.objects.all().order_by("date")
    serializer_class = HourDataSerializer


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class DayViewSet(viewsets.ModelViewSet):
    queryset = Day.objects.all().order_by("date")
    serializer_class = DaySerializer
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


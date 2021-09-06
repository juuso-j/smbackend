from django.shortcuts import render
import requests

from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import (
    Station,
    HourData, 
    DayData,
    WeekData,
    MonthData,
    YearData,
    Day,
    Week,
    Month, 
    Year
)
from .serializers import (
    StationSerializer,
    HourDataSerializer,
    DayDataSerializer,
    WeekDataSerializer,
    MonthDataSerializer,
    MonthSerializer,
    DaySerializer, 
    WeekSerializer,
)


#class HourDataViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
class HourDataViewSet(viewsets.ReadOnlyModelViewSet):
    
    queryset = HourData.objects.all()
    serializer_class = HourDataSerializer

    @action(detail=False, methods=["get"])
    def get_hour_data(self, request):
        date = request.query_params.get("date", None)
        station_id = request.query_params.get("station_id")
        if date is None or station_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        queryset = HourData.objects.get(station_id=station_id, day__date=date)
        serializer = HourDataSerializer(queryset, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DayDataViewSet(viewsets.ReadOnlyModelViewSet):
    
    queryset = DayData.objects.all().order_by("day__date")
    serializer_class = DayDataSerializer

    @action(detail=False, methods=["get"])
    def get_day_data(self, request):
        date = request.query_params.get("date", None)
        station_id = request.query_params.get("station_id")
        if date is None or station_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        queryset = DayData.objects.get(station_id=station_id, day__date=date)
        serializer = DayDataSerializer(queryset, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class WeekDataViewSet(viewsets.ModelViewSet):
    queryset = WeekData.objects.all().order_by("id")
    serializer_class = WeekDataSerializer




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
    


class MonthViewSet(viewsets.ModelViewSet):
    queryset = Month.objects.all()
    serializer_class = MonthSerializer


class MonthDataViewSet(viewsets.ModelViewSet):
    queryset = MonthData.objects.all()
    serializer_class = MonthDataSerializer


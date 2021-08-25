from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.response import Response
from .models import Day, Location
from .serializers import DaySerializer, LocationSerializer

class DayViewSet(viewsets.ModelViewSet):
    queryset = Day.objects.all().order_by("date")
    serializer_class = DaySerializer

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.response import Response
from .models import Day
from .serializers import DaySerializer

class DayViewSet(viewsets.ModelViewSet):
    queryset = Day.objects.all()
    serializer_class = DaySerializer

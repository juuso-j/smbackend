from services.api import UnitSerializer
from eco_counter.api import serializers
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import (
    Unit,
    ChargingStationContent,
    Geometry,
)
from .serializers import(    
    UnitSerializer,
    GeometrySerializer,
    ChargingStationContentSerializer,
)


class UnitViewSet(viewsets.ReadOnlyModelViewSet):
    
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    @action(detail=False, methods=["get"])
    def get_charging_stations(self, request):
        queryset = Unit.objects.filter(content_type=Unit.CHARGING_STATION)
        breakpoint()
        pass


class GeometryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Geometry.objects.all()
    serializer_class = GeometrySerializer


class ChargingStationContentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ChargingStationContent.objects.all()
    serializer_class = ChargingStationContentSerializer
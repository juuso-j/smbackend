from django.contrib.gis.gdal.error import GDALException
from mockup.models.content import GasFillingStationContent
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
    ChargingStationSerializer,
    GasFillingStationContentSerializer,
    GasFillingStationSerializer,
)


class UnitViewSet(viewsets.ReadOnlyModelViewSet):
    
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    
    @action(detail=False, methods=["get"])
    # TODO add @decorator to wrapp and refactor
    def get_charging_stations(self, request):
        queryset = Geometry.objects.filter(unit__content_type=Unit.CHARGING_STATION)
        srid = request.query_params.get("srid", None)
        if srid:
            try:
                for elem in queryset:
                    elem.geometry.transform(srid)
            except GDALException:
                return Response("Invalid srid.", status=status.HTTP_400_BAD_REQUEST)
        #serializer = ChargingStationContentSerializer(queryset, many=True)
        serializer = ChargingStationSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["get"])
    def get_gas_filling_stations(self, request):
        queryset = Geometry.objects.filter(unit__content_type=Unit.GAS_FILLING_STATION)
        serializer = GasFillingStationSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
  

class GeometryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Geometry.objects.all()
    serializer_class = GeometrySerializer


class ChargingStationContentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ChargingStationContent.objects.all()
    serializer_class = ChargingStationContentSerializer

class GasFillingStationtContentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GasFillingStationContent.objects.all()
    serializer_class = GasFillingStationContentSerializer
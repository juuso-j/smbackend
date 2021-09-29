import sys
from django.contrib.gis.gdal.error import GDALException
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import (
    Unit,
    ContentTypes,
    GasFillingStationContent,
    ChargingStationContent,
    Geometry,
)

from .serializers import(    
    UnitSerializer,
    GeometrySerializer,
    ContentTypesSerializer,
    ChargingStationContentSerializer,
    ChargingStationSerializer,
    GasFillingStationContentSerializer,
    GasFillingStationSerializer,
)

class UnitViewSet(viewsets.ReadOnlyModelViewSet):
    
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    def get_station_queryset(self, contet_type, request):
        queryset = Geometry.objects.filter(unit__type_name=contet_type)
        srid = request.query_params.get("srid", None)
        if srid:
            try:
                for elem in queryset:
                    elem.geometry.transform(srid)
            except GDALException:
                return Response("Invalid srid.", status=status.HTTP_400_BAD_REQUEST)
        return queryset

    @action(detail=False, methods=["get"])
    # TODO add @decorator to wrap functionality and refactor
    def get_charging_stations(self, request):
        # queryset = Geometry.objects.filter(unit__type_name=Unit.CHARGING_STATION)
        # srid = request.query_params.get("srid", None)
        # if srid:
        #     try:
        #         for elem in queryset:
        #             elem.geometry.transform(srid)
        #     except GDALException:
        #         return Response("Invalid srid.", status=status.HTTP_400_BAD_REQUEST)
        queryset = self.get_station_queryset(Unit.CHARGING_STATION, request)
        serializer = ChargingStationSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["get"])
    def get_gas_filling_stations(self, request):
        queryset = Geometry.objects.filter(unit__type_name__type_name=ContentTypes.GAS_FILLING_STATION)
        serializer = GasFillingStationSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request):
        type_name = request.query_params.get("type_name", None)
        srid = request.query_params.get("srid", None)
      
        if not type_name:
            queryset = Geometry.objects.all()
            serializer = UnitSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            queryset = Geometry.objects.filter(unit__content_type__type_name=type_name)
            if srid:
                try:
                    for elem in queryset:
                        elem.geometry.transform(srid)
                except GDALException:
                    return Response("Invalid SRID.", status=status.HTTP_400_BAD_REQUEST)
            class_name = ContentTypes.objects.get(type_name=type_name).class_name
            serializer_class = getattr(sys.modules[__name__], class_name+"Serializer")
            serializer = serializer_class(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


class GeometryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Geometry.objects.all()
    serializer_class = GeometrySerializer


class ContentTypesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ContentTypes.objects.all()
    serializer_class = ContentTypesSerializer


class ChargingStationContentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ChargingStationContent.objects.all()
    serializer_class = ChargingStationContentSerializer


class GasFillingStationtContentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GasFillingStationContent.objects.all()
    serializer_class = GasFillingStationContentSerializer
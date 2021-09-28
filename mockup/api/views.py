import sys
from django.contrib.gis.gdal.error import GDALException
from mockup.models.content import GasFillingStationContent
from services.api import UnitSerializer
from eco_counter.api import serializers
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import (
    Unit,
    ContentTypes,
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
    def get_station_queryset(self, contet_type, request):
        queryset = Geometry.objects.filter(unit__content_type=contet_type)
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
        # queryset = Geometry.objects.filter(unit__content_type=Unit.CHARGING_STATION)
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
        queryset = Geometry.objects.filter(unit__content_type__short_name=ContentTypes.GAS_FILLING_STATION)
        serializer = GasFillingStationSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request):
        content_type = request.query_params.get("content_type", None)
        if not content_type:
            print("Not content_Type")
            queryset = Unit.objects.all()
            serializer = UnitSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            queryset = Geometry.objects.filter(unit__content_type__short_name=content_type)
            srid = request.query_params.get("srid", None)
            if srid:
                try:
                    for elem in queryset:
                        elem.geometry.transform(srid)
                except GDALException:
                    return Response("Invalid SRID.", status=status.HTTP_400_BAD_REQUEST)
            class_name = ContentTypes.objects.get(short_name=content_type).class_name
            # serializer_class = getattr(sys.modules[__name__], class_name+"Serializer")
            # serializer = serializer_class(queryset, many=False)
            # return Response(serializer.data, status=status.HTTP_200_OK)

            # breakpoint()

            if content_type==ContentTypes.GAS_FILLING_STATION:
                serializer = GasFillingStationSerializer(queryset, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            elif content_type==ContentTypes.GAS_FILLING_STATION:
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
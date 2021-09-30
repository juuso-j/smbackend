import sys
from django.contrib.gis.gdal.error import GDALException
from rest_framework import status, viewsets
from rest_framework.response import Response
from .utils import transform_queryset
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
        
    def retrieve(self, request, pk=None):
        unit = Unit.objects.get(pk=pk)
        srid = request.query_params.get("srid", None)
        queryset = unit.geometries.all()
        if srid:
            success, queryset = transform_queryset(srid, queryset)
            if not success:
                return Response("Invalid SRID.", status=status.HTTP_400_BAD_REQUEST)
        serializer = UnitSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def list(self, request):
        type_name = request.query_params.get("type_name", None)        
        srid = request.query_params.get("srid", None)
     
        if not type_name:
            queryset = Geometry.objects.all()
            if srid:
                success, queryset = transform_queryset(srid, queryset)
                if not success:
                    return Response("Invalid SRID.", status=status.HTTP_400_BAD_REQUEST)

            page = self.paginate_queryset(queryset)
            serializer = UnitSerializer(queryset, many=True)
            response = self.get_paginated_response(serializer.data)           
            return Response(response.data, status=status.HTTP_200_OK)
        else:
            if not ContentTypes.objects.filter(type_name=type_name).exists():
                return Response("type_name does not exist.", status=status.HTTP_400_BAD_REQUEST)

            queryset = Geometry.objects.filter(unit__content_type__type_name=type_name)
            if srid:
                success, queryset = transform_queryset(srid, queryset)
                if not success:
                    return Response("Invalid SRID.", status=status.HTTP_400_BAD_REQUEST)
            page = self.paginate_queryset(queryset)
            class_name = ContentTypes.objects.get(type_name=type_name).class_name
            serializer_class = getattr(sys.modules[__name__], class_name+"Serializer")
            serializer = serializer_class(queryset, many=True)
            response = self.get_paginated_response(serializer.data)           
            return Response(response.data, status=status.HTTP_200_OK)


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
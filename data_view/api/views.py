import sys
from django.contrib.gis.gdal.error import GDALException
from rest_framework import status, viewsets
from rest_framework.response import Response
from .utils import transform_queryset, transform_group_queryset
from ..models import (
    UnitGroup,
    Unit,
    ContentTypes,
    GroupTypes,
    GasFillingStationContent,
    ChargingStationContent,
    #Geometry,
)
from .serializers import(   
    UnitGroupSerializer, 
    UnitSerializer,
    #GeometrySerializer,
    GroupTypesSerializer,
    ContentTypesSerializer,
    ChargingStationContentSerializer,
    ChargingStationSerializer,
    GasFillingStationContentSerializer,
    GasFillingStationSerializer,
)
#from data_view.api import serializers

class UnitGroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UnitGroup.objects.all()
    serializer_class = UnitGroupSerializer

    def list(self, request):
        type_name = request.query_params.get("type_name", None)        
        srid = request.query_params.get("srid", None)
        queryset = None
        if not type_name:
            queryset = UnitGroup.objects.all()
        else:
            if not GroupTypes.objects.filter(type_name=type_name).exists():
                return Response("type_name does not exist.", status=status.HTTP_400_BAD_REQUEST)

            queryset = UnitGroup.objects.filter(group_type__type_name=type_name)
     
        if srid: 
            #success, queryset = transform_group_queryset(srid, queryset)
            trans_qs = UnitGroup.objects.none()
            ids = []
            # for i,elem in enumerate(queryset):
            #     # qs returns OK tranformed coords
            #     success, qs = transform_queryset(srid, elem.units.all())
            #     queryset[i].units.set(qs) # EI VITTU TEE MITÄÄN
            for i,elem in enumerate(queryset):
                for j, unit in enumerate(elem.units.all()):
                    setattr(queryset[i].units.all()[j],"geometry", unit.geometry.transform(srid))    
            
            # if not success:
            #     return Response("Invalid SRID.", status=status.HTTP_400_BAD_REQUEST)
    
        page = self.paginate_queryset(queryset)
        serializer = UnitGroupSerializer(queryset, many=True)
        response = self.get_paginated_response(serializer.data)           
        return Response(response.data, status=status.HTTP_200_OK)

    

class UnitViewSet(viewsets.ReadOnlyModelViewSet):
    
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer     
        
    def retrieve(self, request, pk=None):
        unit = Unit.objects.get(pk=pk)
        srid = request.query_params.get("srid", None)
        if srid:
            try:
                unit.geometry.transform(srid)
            except GDALException:
                return Response("Invalid SRID.", status=status.HTTP_400_BAD_REQUEST)
        serializer = UnitSerializer(unit, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def list(self, request):
        type_name = request.query_params.get("type_name", None)        
        srid = request.query_params.get("srid", None)
        queryset = None
        serializer = None 
        if not type_name:
            queryset = Unit.objects.all()
            if srid:
                success, queryset = transform_queryset(srid, queryset)
                if not success:
                    return Response("Invalid SRID.", status=status.HTTP_400_BAD_REQUEST)

            page = self.paginate_queryset(queryset)
            serializer = UnitSerializer(queryset, many=True)
        else:
            if not ContentTypes.objects.filter(type_name=type_name).exists():
                return Response("type_name does not exist.", status=status.HTTP_400_BAD_REQUEST)

            queryset = Unit.objects.filter(content_type__type_name=type_name)
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


# class GeometryViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = Geometry.objects.all()
#     serializer_class = GeometrySerializer


class GroupTypesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GroupTypes.objects.all()
    serializer_class = GroupTypesSerializer
   
        #wueryset = UnitGroup.objects.filter

class ContentTypesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ContentTypes.objects.all()
    serializer_class = ContentTypesSerializer


class ChargingStationContentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ChargingStationContent.objects.all()
    serializer_class = ChargingStationContentSerializer


class GasFillingStationtContentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GasFillingStationContent.objects.all()
    serializer_class = GasFillingStationContentSerializer
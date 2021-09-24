from mockup.models.content import GasFillingStationContent
from django.contrib.gis.geos import geometry
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from ..models import (
    Unit,
    Geometry,
    ChargingStationContent
)



class UnitSerializer(serializers.ModelSerializer):

    geometries = serializers.StringRelatedField(many=True)
    class Meta:
        model = Unit
        fields = [
            "created_time",
            "is_active",
            "content_type",
            "geometries",
        ]

class GeometrySerializer(GeoFeatureModelSerializer):
    unit = UnitSerializer()
    class Meta:
        model = Geometry
        geo_field = "geometry"
        fields = [
            "geometry",
            "unit",
        ]

class ChargingStationContentSerializer(serializers.ModelSerializer):
   
#    unit = UnitSerializer()
#    geometry = serializers.SerializerMethodField()
#    geometries = serializers.PrimaryKeyRelatedField(many=False, queryset=Geometry.objects.all())
#    breakpoint()
    class Meta:
        model = ChargingStationContent
        fields = [
            "name",
            "address",
            "url",
            "charger_type",            
            ]

class GasFillingStationContentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = GasFillingStationContent
        fields = [
            "name",
            "address",
            "operator",
            "lng_cng",            
            ]

class ChargingStationSerializer(GeoFeatureModelSerializer):
    unit = UnitSerializer()
    charging_station_content = ChargingStationContentSerializer(many=False, read_only=True, source="unit.charging_station_content")
    class Meta:
        model = Geometry
        geo_field = "geometry"
        fields = [
            "geometry",
            "unit",
            "charging_station_content",
        ]

class GasFillingStationSerializer(GeoFeatureModelSerializer):
    unit = UnitSerializer()
    gas_filling_station_content = GasFillingStationContentSerializer(many=False, read_only=True, source="unit.gas_filling_station_content")
    class Meta:
        model = Geometry
        geo_field = "geometry"
        fields = [
            "geometry",
            "unit",
            "gas_filling_station_content",
        ]


   
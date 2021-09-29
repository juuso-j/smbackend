from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from . import UnitInfoSerializer

from ...models import(
    Geometry,
    ChargingStationContent,
)


class ChargingStationContentSerializer(serializers.ModelSerializer):
   

    class Meta:
        model = ChargingStationContent
        fields = [
            "name",
            "address",
            "url",
            "charger_type",            
            ]


class ChargingStationSerializer(GeoFeatureModelSerializer):
    unit = UnitInfoSerializer()
    charging_station_content = ChargingStationContentSerializer(many=False, read_only=True, source="unit.charging_station_content")
    class Meta:
        model = Geometry
        geo_field = "geometry"
        fields = [
            "geometry",
            "unit",
            "charging_station_content",
        ]

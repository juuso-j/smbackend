from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from . import UnitInfoSerializer
from ...models import(
    GasFillingStationContent,
    Geometry
)

class GasFillingStationContentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = GasFillingStationContent
        fields = [
            "name",
            "address",
            "operator",
            "lng_cng",            
            ]



class GasFillingStationSerializer(GeoFeatureModelSerializer):
    unit = UnitInfoSerializer()
    gas_filling_station_content = GasFillingStationContentSerializer(many=False, read_only=True, source="unit.gas_filling_station_content")
    class Meta:
        model = Geometry
        geo_field = "geometry"
        fields = [
            "geometry",
            "unit",
            "gas_filling_station_content",
        ]


   
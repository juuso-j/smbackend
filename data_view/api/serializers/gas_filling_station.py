from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from . import UnitInfoSerializer
from ...models import(
    GasFillingStationContent,
    Unit
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
    gas_filling_station_content = GasFillingStationContentSerializer(many=False, read_only=True)
    class Meta:
        model = Unit
        geo_field = "geometry"
        fields = [
            "geometry",
            "gas_filling_station_content",
        ]


   
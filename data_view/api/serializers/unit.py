import json
from django.core import serializers as django_serializers
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .content_types import ContentTypesSerializer
from ...models import(
    Unit,
    ContentTypes,
    Geometry,
)


class UnitInfoSerializer(serializers.ModelSerializer):
  
    class Meta:
        model = Unit
        fields = [
            "created_time",
            "is_active",
        ]    


class UnitSerializer(GeoFeatureModelSerializer):
    unit = UnitInfoSerializer()
    content_type = ContentTypesSerializer(many=False, read_only=True, source="unit.content_type")
    content = serializers.SerializerMethodField()
    class Meta: 
        model = Geometry
        geo_field = "geometry"
        fields = [
            "geometry",
            "content_type",
            "unit",
            "content"
        ]

    def get_content(self, obj):
        content = None
        if obj.unit.content_type.type_name == ContentTypes.GAS_FILLING_STATION:
            content = obj.unit.gas_filling_station_content           
        elif obj.unit.content_type.type_name == ContentTypes.CHARGING_STATION:
            content = obj.unit.charging_station_content 

        ser_data = django_serializers.serialize("json",[content,])
        return json.loads(ser_data) 

from rest_framework import serializers

from ..models import (
    Unit,
    Geometry,
    ChargingStationContent
)



class UnitSerializer(serializers.ModelSerializer):

    class Meta:
        model = Unit
        fields = "__all__"


class ChargingStationContentSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChargingStationContent
        fields = "__all__"

class GeometrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Geometry
        fields = "__all__"
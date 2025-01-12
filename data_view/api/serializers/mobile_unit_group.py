from data_view.api.serializers.mobile_unit import MobileUnitSerializer
from rest_framework import serializers
from . import MobileUnitSerializer
from ...models import(
    MobileUnitGroup
)

class MobileUnitGroupSerializer(serializers.ModelSerializer):
    units = MobileUnitSerializer(
        many=True,
        read_only=True,      
    )

    class Meta:
        model = MobileUnitGroup
        fields = [
            "id",
            "name",
            "name_fi",
            "name_sv",
            "name_en",            
            "description",
            "description_fi",
            "description_sv",            
            "description_en",
            "units"
        ]
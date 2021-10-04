from data_view.api.serializers.unit import UnitSerializer
from rest_framework import serializers
from . import UnitSerializer
from ...models import(
    UnitGroup
)

class UnitGroupSerializer(serializers.ModelSerializer):
    units = UnitSerializer(
        many=True,
        read_only=True,      
    )

    class Meta:
        model = UnitGroup
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
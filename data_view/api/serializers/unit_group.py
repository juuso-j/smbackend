from data_view.api.serializers.unit import UnitSerializer
from rest_framework import serializers
from . import UnitSerializer
from ...models import(
    UnitGroup
)

class UnitGroupSerializer(serializers.ModelSerializer):
    unit = UnitSerializer(
        many=True,
        read_only=True,
        source="units"
    )

    class Meta:
        model = UnitGroup
        fields = [
            "id",
            "unit"
        ]
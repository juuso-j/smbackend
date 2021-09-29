from rest_framework_gis.serializers import GeoFeatureModelSerializer
from . import UnitInfoSerializer
from ...models import Geometry


class GeometrySerializer(GeoFeatureModelSerializer):
    unit = UnitInfoSerializer()
    class Meta:
        model = Geometry
        geo_field = "geometry"
        fields = [
            "geometry",
            "unit",
        ]
 
from io import StringIO
import pytest
from django.conf import settings
from django.core.management import call_command
from django.contrib.gis.geos import Point
from data_view.models import (
    Unit,
    ContentTypes,
    ChargingStationContent,
#    Geometry
)

def import_command(*args, **kwargs):
        out = StringIO()
        call_command(
            "import_charging_stations",
            *args,
            stdout=out,
            stderr=StringIO(),
            **kwargs,
        )
        return out.getvalue()

@pytest.mark.django_db
def test__importer():
    out = import_command(test_mode="charging_stations.json")
    assert ContentTypes.objects.filter(type_name=ContentTypes.CHARGING_STATION).count() == 1
    assert Unit.objects.filter(content_type__type_name=ContentTypes.CHARGING_STATION).count() == 2
    assert ChargingStationContent.objects.all().count() == 2
    assert ChargingStationContent.objects.filter(name__contains="ABC Tammisilta")
    assert Geometry.objects.all().count() == 2
    geom_obj = Geometry.objects.get(unit__charging_station_content__name__contains="ABC")
    point = Point(258291.19004666203, 6708817.731819544, srid=settings.DEFAULT_SRID) 
    assert geom_obj.geometry.coords == point.coords
    out = import_command(test_mode="charging_stations.json")
    assert ContentTypes.objects.filter(type_name=ContentTypes.CHARGING_STATION).count() == 1
    assert Unit.objects.filter(content_type__type_name=ContentTypes.CHARGING_STATION).count() == 2
    assert ChargingStationContent.objects.all().count() == 2
    assert Geometry.objects.all().count() == 2
    

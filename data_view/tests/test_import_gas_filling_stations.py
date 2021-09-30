from io import StringIO
import pytest
from django.conf import settings
from django.core.management import call_command
from django.contrib.gis.geos import Point
from data_view.models import (
    Unit,
    ContentTypes,
    GasFillingStationContent,
    Geometry
)

def import_command(*args, **kwargs):
        out = StringIO()
        call_command(
            "import_gas_filling_stations",
            *args,
            stdout=out,
            stderr=StringIO(),
            **kwargs,
        )
        return out.getvalue()

@pytest.mark.django_db
def test__importer():
    out = import_command(test_mode="gas_filling_stations.json")
    assert ContentTypes.objects.filter(type_name=ContentTypes.GAS_FILLING_STATION).count() == 1
    assert Unit.objects.filter(content_type__type_name=ContentTypes.GAS_FILLING_STATION).count() == 2
    assert GasFillingStationContent.objects.all().count() == 2
    assert GasFillingStationContent.objects.filter(name__contains="Turku Satama")
    assert GasFillingStationContent.objects.filter(name__contains="Raisio Kuninkoja")
    assert Geometry.objects.all().count() == 2
    geom_obj = Geometry.objects.get(unit__gas_filling_station_content__name__contains="Turku Satama")
    assert geom_obj.unit.gas_filling_station_content.operator == "Gasum"
    point = Point(2472735.3962113541, 8500004.76446491, srid=3857) 
    point.transform(settings.DEFAULT_SRID)
    assert geom_obj.geometry.coords == point.coords
    out = import_command(test_mode="gas_filling_stations.json")
    assert ContentTypes.objects.filter(type_name=ContentTypes.GAS_FILLING_STATION).count() == 1
    assert Unit.objects.filter(content_type__type_name=ContentTypes.GAS_FILLING_STATION).count() == 2
    assert GasFillingStationContent.objects.all().count() == 2
    assert Geometry.objects.all().count() == 2

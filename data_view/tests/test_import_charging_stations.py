from io import StringIO
import pytest
from django.core.management import call_command
from data_view.models import (
    MobileUnit,
    ContentTypes,
    ChargingStationContent,
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
def test_importer():

    out = import_command(test_mode="charging_stations.json")
    assert ContentTypes.objects.filter(type_name=ContentTypes.CHARGING_STATION).count() == 1
    assert MobileUnit.objects.filter(content_type__type_name=ContentTypes.CHARGING_STATION).count() == 2
    assert MobileUnit.objects.get(name="AimoPark Stockmann Turku")
    unit = MobileUnit.objects.get(name="Hotel Kakola")
    assert unit
    # Transform to source data srid
    unit.geometry.transform(4326)
    assert pytest.approx(unit.geometry.x, 0.0001) == 22.247
    assert ChargingStationContent.objects.all().count() == 2  
    content = ChargingStationContent.objects.get(mobile_unit__name="Hotel Kakola") 
    assert content.charger_type == "Type2"
    assert content.mobile_unit == unit
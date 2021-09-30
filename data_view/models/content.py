import uuid
from django.contrib.gis.db import models
from django.contrib.contenttypes.fields import GenericRelation
from . import Unit


class Station(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=64, null=True)
    address = models.CharField(max_length=128, null=True)

    class Meta:
        abstract = True


class ChargingStationContent(Station):
    url = models.URLField(null=True)
    charger_type = models.CharField(max_length=32, null=True)
    unit = models.OneToOneField(
        Unit, 
        related_name="charging_station_content",
        on_delete=models.CASCADE, 
        null=True)
 

class GasFillingStationContent(Station):
    lng_cng = models.CharField(max_length=8, null=True)
    operator = models.CharField(max_length=32, null=True)
    # units = GenericRelation(
    #     Unit,
    #     content_type_field="content_type",
    #     object_id_field="content_id",
    #     related_query_name="contents"
    #   )
    unit = models.OneToOneField(
        Unit, 
        related_name="gas_filling_station_content",
        on_delete=models.CASCADE, 
        null=True)
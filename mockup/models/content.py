import uuid
from django.contrib.gis.db import models
from django.contrib.contenttypes.fields import GenericRelation
from . import Unit


class Station(models.Model):
    name = models.CharField(max_length=100, null=True)
    address = models.CharField(max_length=100, null=True)

    class Meta:
        abstract = True


class ChargingStationContent(Station):
    url = models.URLField(null=True)
    charger_type = models.CharField(max_length=30, null=True)
    unit = models.OneToOneField(
        Unit, 
        related_name="charging_station_content",
        on_delete=models.CASCADE, 
        null=True)
    # units = GenericRelation(
    #     Unit,
    #     content_type_field="content_type",
    #     object_id_field="content_id",
    #     related_query_name="contents"
    #   )


class GasFillingStationContent(Station):
    lng_cng = models.CharField(max_length=10, null=True)
    operator = models.CharField(max_length=30, null=True)
    unit = models.OneToOneField(
        Unit, 
        related_name="gas_filling_station_content",
        on_delete=models.CASCADE, 
        null=True)
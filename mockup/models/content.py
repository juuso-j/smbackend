from django.contrib.gis.db import models
from django.contrib.contenttypes.fields import GenericRelation
from . import Unit


class Station(models.Model):
    name = models.CharField(max_length=30, null=True)
    address = models.CharField(max_length=100, null=True)
    url = models.URLField(null=True)
    
    class Meta:
        abstract = True


class ChargingStationContent(models.Model):
    name = models.CharField(max_length=30, null=True)
    address = models.CharField(max_length=100, null=True)
    url = models.URLField(null=True)

    charger_type = models.CharField(max_length=30, null=True)
    units = GenericRelation(
        Unit,
        content_type_field="content_type",
        object_id_field="content_id",
        related_query_name="chargingstationcontent",
        related_name="chargingstationcontents"
        )


class GasStationContent(Station):
    lng_cng = models.CharField(max_length=10, null=True)
    operator = models.CharField(max_length=30, null=True)

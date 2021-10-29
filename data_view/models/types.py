import uuid
from django.contrib.gis.db import models

class BaseTypes(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=64, null=True)
    class_name = models.CharField(max_length=64, null=True)
    description = models.TextField(null=True)

    class Meta:
        abstract = True

class ContentTypes(BaseTypes):
    CHARGING_STATION = "CGS"
    GAS_FILLING_STATION = "GFS"
    WALKING_ROUTE = "WGR"
    STATUE = "STE"
    CONTENT_TYPES = {
        CHARGING_STATION: "ChargingStation",
        GAS_FILLING_STATION: "GasFillingStation",
        WALKING_ROUTE: "WalkingRoute",
        STATUE: "Statue"
    }
    type_name = models.CharField(
        max_length=3, 
        choices=[(k,v) for k,v in CONTENT_TYPES.items()], 
        null=True
    )
  


class GroupTypes(BaseTypes):
    CULTURE_ROUTE = "CER"

    GROUP_TYPES = {
        CULTURE_ROUTE: "CultureRoute",
    }
    type_name = models.CharField(
        max_length=3, 
        choices= [(k,v) for k,v in GROUP_TYPES.items()], 
        null=True
    )
    
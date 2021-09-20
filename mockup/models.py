from django.contrib.gis.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
#from django.contrib.gis.db.models.fields import PointField

GEOMETRY_MODELS_LIST = (
        models.Q(model="pointgeometry") | 
        models.Q(model="multipolygongeometry") |
        models.Q(model="polygongeometry") |
        models.Q(model="linestringgeometry")        
    )

CONTENT_MODELS_LIST=(
    models.Q(model="charginstationcontent") |
    models.Q(model="gasstationcontent") | 
    models.Q(model="routecontent") |
    models.Q(model="parkingareacontent") 
)

UNIT_TYPES = (
    (0, "CHARING_STATION"),
    (1, "GAS_STATION"),
    (2, "ROUTE"), # Paavonpolku, kulttuurireitti etc..
    (3, "PARKING_AREA"),
)

# The main class that has a relation to a geometry and to a content.
# The type of the relatated classes depends on the UNIT_TYPE.
# e.g. Route("Paavonplku XX") has a relation to LineStringGeometry and RouteContent
class Unit(models.Model):
    is_active = models.BooleanField(default=True)
    created_time = models.DateTimeField(
        null=True
    )
    last_modified_time = models.DateTimeField(
        null=True
    )
    #name = models.CharField(max_length=100)
    geometry_ct = models.ForeignKey(
        ContentType, 
        blank=True, 
        null=True, 
        related_name="unit",
        related_query_name="geom_obj",
        on_delete=models.CASCADE,
        limit_choices_to=GEOMETRY_MODELS_LIST,)
    geometry_id = models.UUIDField(null=True, blank=True)
    geometry = GenericForeignKey("geometry_ct", "geometry_id")
    type = models.PositiveSmallIntegerField(choices=UNIT_TYPES, null=True)
    content_ct = models.ForeignKey(
        ContentType, 
        blank=True, 
        null=True, 
        related_query_name="content_obj",
        on_delete=models.CASCADE,
        limit_choices_to=CONTENT_MODELS_LIST,)
    content_id = models.UUIDField(null=True, blank=True)
    content = GenericForeignKey("content_ct", "content_id")


# Various geometry classes
class PointGeometry(models.Model):
    geometry = models.PointField()


class PolygonGeometry(models.Model):
    geometry = models.PolygonField()


class MultiPolygonGeometry(models.Model):
    geometry = models.MultiPolygonField()


class LineStringGeometry(models.Model):
    geometry = models.LineStringField()


# Various content classes 
class RouteContent(models.Model):
    description = models.TextField(null=True)


class ParkingAreaContent(models.Model):
    capacity = models.PositiveSmallIntegerField(null=True)


class Station(models.Model):
    name = models.CharField(max_length=30, null=True)
    address = models.CharField(max_length=100, null=True)
    url = models.URLField(null=True)
    
    class Meta:
        abstract = True


class CharginStationContent(Station):
    charger_type = models.CharField(max_length=10, null=True)


class GasStationContent(Station):
    pass







"""
from mockup.models import *
from django.contrib.gis.geos import Polygon, Point
ls = PolygonGeometry.objects.create(geom=Polygon( ((0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0), (0.0, 0.0)) ))
lp = PointGeometry.objects.create(geom=Point(2,2))
unit =Unit.objects.create()
unit.geometry = lp
unit.save()
route = RouteContent.objects.create(description="Paavonpolku")
unit.content = route
unit.save()
"""
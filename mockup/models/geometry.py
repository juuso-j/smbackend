from django.contrib.gis.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.gis.geos import geometry
from . import Unit


class Geometry(models.Model):
    geometry = models.GeometryField(null=True)
    unit = models.OneToOneField(
        Unit, 
        related_name="geometries",
        on_delete=models.CASCADE, 
        null=True
    )

# Various geometry classes
class PointGeometry(models.Model):
    geometry = models.PointField()
    unit = models.OneToOneField(
        Unit, 
        related_name="point_geometries",
        on_delete=models.CASCADE, 
        null=True)
   

class PolygonGeometry(models.Model):
    geometry = models.PolygonField()
    unit = models.OneToOneField(
        Unit, 
        related_name="polygon_geometries",
        on_delete=models.CASCADE, 
        null=True)
   

class MultiPolygonGeometry(models.Model):
    geometry = models.MultiPolygonField()


class LineStringGeometry(models.Model):
    geometry = models.LineStringField()

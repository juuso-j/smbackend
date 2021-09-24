from django.contrib.gis.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.gis.geos import geometry
from . import Unit


class Geometry(models.Model):
    # More about EPSG:3879 https://epsg.io/3879
    #geometry = models.GeometryField(srid=3879, null=True)
    geometry = models.GeometryField(srid=4326, null=True)
 
    unit = models.ForeignKey(
        Unit, 
        related_name="geometries",
        on_delete=models.CASCADE, 
        null=True
    )   

    def __str__(self):
        return str(self.geometry)



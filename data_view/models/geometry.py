from django.contrib.gis.db import models
from django.conf import settings
from . import Unit


class Geometry(models.Model):
    
    """
    Portions of the earth’s surface may projected onto a two-dimensional, 
    or Cartesian, plane. Projected coordinate systems are especially convenient
    for region-specific applications, e.g., if you know that your database 
    will only cover geometries in North Kansas, then you may consider using 
    rojection system specific to that region. Moreover, projected coordinate 
    systems are defined in Cartesian units (such as meters or feet), easing 
    distance calculations.
    """
    # More about EPSG:3879 https://epsg.io/3067
    
    geometry = models.GeometryField(srid=settings.DEFAULT_SRID, null=True)

    unit = models.ForeignKey(
        Unit, 
        related_name="geometries",
        on_delete=models.CASCADE, 
        null=True
    )   

    def __str__(self):
        return str(self.geometry)



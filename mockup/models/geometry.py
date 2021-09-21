from django.contrib.gis.db import models
from django.contrib.contenttypes.fields import GenericRelation
from . import Unit


# Various geometry classes
class PointGeometry(models.Model):
    geometry = models.PointField()
    units = GenericRelation(
        Unit,
        content_type_field="geometry_type",
        object_id_field="geometry_id"
        )


class PolygonGeometry(models.Model):
    geometry = models.PolygonField()


class MultiPolygonGeometry(models.Model):
    geometry = models.MultiPolygonField()


class LineStringGeometry(models.Model):
    geometry = models.LineStringField()

import uuid
from django.conf import settings
from django.contrib.gis.db import models
from . import ContentTypes, GroupTypes


class BaseUnit(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    is_active = models.BooleanField(default=True)
    created_time = models.DateTimeField(
        auto_now_add=True
    )
    name = models.CharField(max_length=64, null=True)
    description=models.TextField(null=True)

    class Meta:
        abstract = True
        ordering = ["created_time"]
 

class UnitGroup(BaseUnit): 
    group_type = models.ForeignKey(
        GroupTypes,
        on_delete=models.CASCADE, 
        null=True, 
        related_name="unit_groups"
    )
    def transform(self):
        for unit in self.units.all():
            unit.geometry.transform(4326)

class Unit(BaseUnit):
    """
    Portions of the earth’s surface may projected onto a two-dimensional, 
    or Cartesian, plane. Projected coordinate systems are especially convenient
    for region-specific applications, e.g., if you know that your database 
    will only cover geometries in North Kansas, then you may consider using 
    rojection system specific to that region. Moreover, projected coordinate 
    systems are defined in Cartesian units (such as meters or feet), easing 
    distance calculations.
    """
    # More about EPSG:3067 https://epsg.io/3067
    
    geometry = models.GeometryField(srid=settings.DEFAULT_SRID, null=True)
    address = models.CharField(max_length=100, null=True)
    content_type = models.ForeignKey(
        ContentTypes,
        on_delete=models.CASCADE, 
        null=True, 
        related_name="units"
    )
    # TODO, NOTE, maybe many-to-many???
    unit_group = models.ForeignKey(
        UnitGroup, 
        on_delete=models.CASCADE,
        null=True,
        related_name="units"
    ) 
   
    def transform(self):
        self.geometry.transform(4326)
        print("transform", self.geometry.coords)
       
    # content_type = models.CharField(
    #     max_length=3, 
    #     choices= [(k,v) for k,v in CONTENT_TYPES.items()], 
    #     null=True
    #     )

    # content_type = models.ForeignKey(
    #     ContentType, 
    #     blank=True, 
    #     null=True, 
    #     # related_name="content_unit",
    #     # related_query_name="contents",
    #     on_delete=models.CASCADE
    #     )
    # content_id = models.PositiveIntegerField(null=True, blank=True)
    # content = GenericForeignKey("content_type", "content_id")



# The main class that has a relation to a geometry and to a content.
# The type of the relatated classes depends on the UNIT_TYPE.
# e.g. Route("Paavonpolku XX") has a relation to LineStringGeometry and RouteContent
# class Unit(models.Model):
#     is_active = models.BooleanField(default=True)
#     created_time = models.DateTimeField(
#         auto_now_add=True
#     )
#     last_modified_time = models.DateTimeField(
#         auto_now=True
#     )
#     #name = models.CharField(max_length=100)
#     geometry_type = models.ForeignKey(
#         ContentType, 
#         blank=True, 
#         null=True, 
#         related_name="geometry_unit",
#         related_query_name="geom_obj",
#         on_delete=models.CASCADE,
#         limit_choices_to=GEOMETRY_MODELS_LIST,)
#     geometry_id = models.PositiveIntegerField(null=True, blank=True)
#     geometry = GenericForeignKey("geometry_type", "geometry_id")
#     type = models.PositiveSmallIntegerField(choices=UNIT_TYPES, null=True)
#     content_type = models.ForeignKey(
#         ContentType, 
#         blank=True, 
#         null=True, 
#         # related_name="content_unit",
#         # related_query_name="contents",
#         on_delete=models.CASCADE
#         )
#     content_id = models.PositiveIntegerField(null=True, blank=True)
#     content = GenericForeignKey("content_type", "content_id")


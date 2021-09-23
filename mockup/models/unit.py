import enum
# from mockup.models.geometry import MultiPolygonGeometry
# from mockup.management.commands.import_charging_stations import CHARGING_STATIONS_URL, GAS_STATIONS_URL
from django.contrib.gis.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# GEOMETRY_MODELS_LIST = (
#         models.Q(model="pointgeometry") | 
#         models.Q(model="multipolygongeometry") |
#         models.Q(model="polygongeometry") |
#         models.Q(model="linestringgeometry")        
#     )

# CONTENT_MODELS_LIST=(
#     models.Q(model="charginstationcontent") |
#     models.Q(model="gasstationcontent") | 
#     models.Q(model="routecontent") |
#     models.Q(model="parkingareacontent") 
# )

# class ContentTypes(enum.Enum):
#     chargin_station = 1
#     gas_station = 2
    


class Unit(models.Model):

    CHARGING_STATION = "CS"
    GAS_STATION = "GS"

    CONTENT_TYPES = [
        (CHARGING_STATION, "ChargingStation"),
        (GAS_STATION, "GasStation"),
    ]

    POINTGEOMETRY = "PT"
    POLYGONGEOMETRY = "PY"
    LINESTRINGGEOMETRY = "LS"
    MULTIPOINTGEOMETRY = "MP"
    MULTIPOLYGONGEOMETRY = "MPY"
    MULTILINESTRINGGEOMETRY = "MLS"

    GEOMETRY_TYPES = (
        (POINTGEOMETRY, "PointGeometry"),
        (POLYGONGEOMETRY, "PolygonGeometry"),
        (LINESTRINGGEOMETRY, "LineStringGeometry"),
        (MULTIPOINTGEOMETRY, "MultiPointGeometry"),
        (MULTIPOLYGONGEOMETRY, "MultiPolygonGeometry"),
        (MULTILINESTRINGGEOMETRY, "MultiLineStringGeometry"),
    )
    is_active = models.BooleanField(default=True)
    created_time = models.DateTimeField(
        auto_now_add=True
    )
    # last_modified_time = models.DateTimeField(
    #     auto_now=True
    # )    
    content_type = models.CharField(max_length=2, choices=CONTENT_TYPES, null=True)
    #geometry_type = models.CharField(max_length=3, choices=GEOMETRY_TYPES, null=True)
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


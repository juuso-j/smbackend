# from django.contrib.gis.db import models


# class ContentTypes(models.Model):
#     CHARGING_STATION = "CGS"
#     GAS_FILLING_STATION = "GFS"
#     CONTENT_TYPES = {
#         CHARGING_STATION: "ChargingStation",
#         GAS_FILLING_STATION: "GasFillingStation",
#     }
#     type_name = models.CharField(
#         max_length=3, 
#         choices= [(k,v) for k,v in CONTENT_TYPES.items()], 
#         null=True
#         )
#     name = models.CharField(max_length=32, null=True)
#     class_name = models.CharField(max_length=32, null=True)
#     description = models.TextField(null=True)

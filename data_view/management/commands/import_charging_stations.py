import os
import logging
import json
from django.core.management import BaseCommand
from data_view.models import ContentTypes
from data_view.importers.utils import fetch_json
from data_view.importers.charging_stations import(
    get_json_filtered_by_location,
    save_to_database,
    CHARGING_STATIONS_URL
)
logger = logging.getLogger("django")

# from django import db
# from django.contrib.gis.geos import Point, Polygon
# from django.conf import settings
# from data_view.models import (
#     Unit,
#     ContentTypes,
#     ChargingStationContent
#     )
# from .utils import fetch_json, delete_tables, GEOMETRY_URL
# logger = logging.getLogger("django")
# CHARGING_STATIONS_URL = "https://services1.arcgis.com/rhs5fjYxdOG1Et61/ArcGIS/rest/services/ChargingStations/FeatureServer/0/query?f=json&where=1%20%3D%201%20OR%201%20%3D%201&returnGeometry=true&spatialRel=esriSpatialRelIntersects&outFields=LOCATION_ID%2CNAME%2CADDRESS%2CURL%2COBJECTID%2CTYPE"

# def get_filtered_json(json_data):
#     geometry_data = fetch_json(GEOMETRY_URL) 
#     polygon = Polygon(geometry_data["features"][0]["geometry"]["coordinates"][0])
#     out_data = []
#     srid = json_data["spatialReference"]["wkid"]
#     for data in json_data["features"]:
#         x = data["geometry"].get("x",0)
#         y = data["geometry"].get("y",0)
#         point = Point(x, y)
#         if polygon.intersects(point):
#             out_data.append(data)
#     logger.info("Filtered: {} charging stations by location to: {}."\
#         .format(len(json_data["features"]), len(out_data)))
        
#     return srid, out_data
        
# @db.transaction.atomic    
# def save_to_database(json_data, srid):
#     description = "Charging stations in province of SouthWest Finland."
#     content_type = ContentTypes.objects.get_or_create(
#         type_name=ContentTypes.CHARGING_STATION,
#         name="Charging Station",
#         class_name=ContentTypes.CONTENT_TYPES[ContentTypes.CHARGING_STATION],
#         description=description
#     )[0]

#     for data in json_data:
#         is_active = True       
#         geometry = data.get("geometry", None)
#         attributes = data.get("attributes", None)
#         if not attributes or not geometry:
#             continue

#         x = geometry.get("x",0)
#         y = geometry.get("y",0)         
#         point = Point(x,y, srid=srid) 
#         point.transform(settings.DEFAULT_SRID)    
#         name = attributes.get("NAME", "")
#         address = attributes.get("ADDRESS", "")
#         url = attributes.get("URL", "")
#         charger_type = attributes.get("TYPE", "")        
#         unit = Unit.objects.create(
#             is_active=is_active,
#             name=name,
#             address=address,
#             geometry=point,
#             content_type=content_type
#         )
#         content = ChargingStationContent.objects.create(
#             unit=unit,
#             url=url,
#             charger_type=charger_type
#         )
       
#     logger.info("Saved charging stations to database.")
            
        # breakpoint()
        # unit1 = Unit.objects.create(content=content)
        #unit2 = Unit.objects.create(geometry=geometry)
        #unit3, created = Unit.objects.update_or_create(type=0,is_active=True, content_id=content.pk, content_type=ContentTypes.objects.get_for_model(ChargingStationContent))
        # breakpoint()
        # unit = Unit.objects.get(content=content)
        # breakpoint()

        # unit, created = Unit.objects.update_or_create(
        #     is_active=True, 
        #     geometry=geometry, 
        #     content=content
        # )
          
    
class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(            
            "--test-mode",             
            nargs="+",
            default=False,
            help="Run script in test mode. Uses Generated pandas dataframe.",
        )       
    
    def handle(self, *args, **options):
        logger.info("Importing charging stations.")
        if options["test_mode"]:
            logger.info("Running charging_station_importer in test mode.")
            f = open(os.getcwd()+"/"+ContentTypes._meta.app_label+"/tests/"+options["test_mode"], "r")
            json_data = json.load(f)
        else:
            logger.info("Fetcing charging stations from: {}"\
                .format(CHARGING_STATIONS_URL))
            json_data = fetch_json(CHARGING_STATIONS_URL)
        filtered_json = get_json_filtered_by_location(json_data)
        #delete_tables(ContentTypes.CHARGING_STATION)
        save_to_database(filtered_json)
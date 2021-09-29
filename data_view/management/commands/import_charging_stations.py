import os
import logging
import json
from django.core.management import BaseCommand
from django import db
from django.contrib.gis.geos import Point, Polygon
from django.conf import settings
from data_view.models import (
    Unit,
    ContentTypes,
    Geometry,
    ChargingStationContent
    )
from .utils import fetch_json, delete_tables, GEOMETRY_URL
logger = logging.getLogger("django")

CHARGING_STATIONS_URL = "https://services1.arcgis.com/rhs5fjYxdOG1Et61/ArcGIS/rest/services/ChargingStations/FeatureServer/0/query?f=json&where=1%20%3D%201%20OR%201%20%3D%201&returnGeometry=true&spatialRel=esriSpatialRelIntersects&outFields=LOCATION_ID%2CNAME%2CADDRESS%2CURL%2COBJECTID%2CTYPE"

#GEOMETRY_URL = "https://data.foli.fi/geojson/bounds" # contains the boundries for location filtering


def get_filtered_json(json_data):
    geometry_data = fetch_json(GEOMETRY_URL) 
    polygon = Polygon(geometry_data["features"][0]["geometry"]["coordinates"][0])
    out_data = []
    srid = json_data["spatialReference"]["wkid"]
    for data in json_data["features"]:
        lon = data["geometry"].get("x",0)
        lat = data["geometry"].get("y",0)
        point = Point(lon, lat)
        if polygon.intersects(point):
            out_data.append(data)
    logger.info("Filtered: {} charging stations by location to: {}."\
        .format(len(json_data["features"]), len(out_data)))
        
    return srid, out_data
        
@db.transaction.atomic    
def save_to_database(json_data, srid):
    description = "Gas filling stations in province of SouthWest Finland."
    content_type = ContentTypes.objects.get_or_create(
        type_name=ContentTypes.CHARGING_STATION,
        name="Gas Filling Station",
        class_name=ContentTypes.CONTENT_TYPES[ContentTypes.CHARGING_STATION],
        description=description
    )[0]

    for data in json_data:
        is_active = True
       
        geometry = data.get("geometry", None)
        attributes = data.get("attributes", None)
        if not attributes or not geometry:
            continue

        x = geometry.get("x",0)
        y = geometry.get("y",0)         
        point = Point(x,y, srid=srid) 
        point.transform(settings.DEFAULT_SRID)    
        name = attributes.get("NAME", "")
        address = attributes.get("ADDRESS", "")
        url = attributes.get("URL", "")
        charger_type = attributes.get("TYPE", "")        
        unit = Unit.objects.create(
            is_active=is_active,
            content_type=content_type
        )
        content = ChargingStationContent.objects.create(
            unit=unit,
            name=name,
            address=address,
            url=url,
            charger_type=charger_type
        )
        geometry = Geometry.objects.create(
            unit=unit,
            geometry=point
        )
    logger.info("Saved charging stations to database.")
            
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
        srid, filtered_json = get_filtered_json(json_data)
        delete_tables(ContentTypes.CHARGING_STATION)
        save_to_database(filtered_json, srid)
import os
import json
import logging
from django.contrib.gis.geos import GEOSGeometry, Point, Polygon
from django.core.management import BaseCommand
from django import db

from mockup.models import Unit, Geometry, GasFillingStationContent
from .utils import fetch_json,delete_tables, GEOMETRY_URL
logger = logging.getLogger("django")

GAS_FILLING_STATIONS_URL = "https://services1.arcgis.com/rhs5fjYxdOG1Et61/ArcGIS/rest/services/GasFillingStations/FeatureServer/0/query?f=json&where=1%3D1&outFields=OPERATOR%2CLAT%2CLON%2CSTATION_NAME%2CADDRESS%2CCITY%2CZIP_CODE%2CLNG_CNG%2CObjectId"


def get_filtered_json(json_data):
    geometry_data = fetch_json(GEOMETRY_URL) 
    polygon = Polygon(geometry_data["features"][0]["geometry"]["coordinates"][0])
    out_data = []
    #wkid = json_data["spatialReference"]["wkid"]
    for data in json_data["features"]:
        lon = data["attributes"].get("LON",0)
        lat = data["attributes"].get("LAT",0)
        point = Point(lon, lat)
        if polygon.intersects(point):
            out_data.append(data)
    logger.info("Filtered: {} gas filling stations by location to: {}."\
        .format(len(json_data["features"]), len(out_data)))
    return out_data

@db.transaction.atomic    
def save_to_database(json_data):
    #print(wkid)
    for data in json_data:
        is_active = True
        content_type = Unit.GAS_FILLING_STATION 
        lon = data["geometry"].get("x",0)
        lat = data["geometry"].get("y",0)
        point = Point(lon,lat)
        attributes = data.get("attributes", None)
        if not attributes:
            continue

        name = attributes.get("STATION_NAME", "")
        address = attributes.get("ADDRESS", "")
        zip_code = attributes.get("ZIP_CODE", "")
        city = attributes.get("CITY", "")
        address += ", "+zip_code + " " + city
        operator = attributes.get("OPERATOR", "")
        lng_cng = attributes.get("LNG_CNG", "")        
        unit = Unit.objects.create(
            is_active=is_active,
            content_type=content_type
        )
        content = GasFillingStationContent.objects.create(
            unit=unit,
            name=name,
            address=address,
            operator=operator,
            lng_cng=lng_cng
        )
        geometry = Geometry.objects.create(
            unit=unit,
            geometry=point
        )
    logger.info("Saved gas filling stations to database.")

    
class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(            
            "--test-mode",             
            nargs="+",
            default=False,
            help="Run script in test mode. Uses Generated pandas dataframe.",
        )       
    
    def handle(self, *args, **options):
        logger.info("Importing gas filling stations.")
        if options["test_mode"]:
            logger.info("Running gas filling station_importer in test mode.")
            # TODO get current working directory
            f = open(os.getcwd()+"/mockup/tests/"+options["test_mode"], "r")
            json_data = json.load(f)
        else:
            logger.info("Fetcing gas filling stations from: {}"\
                .format(GAS_FILLING_STATIONS_URL))
            json_data = fetch_json(GAS_FILLING_STATIONS_URL)
        filtered_json = get_filtered_json(json_data)
        delete_tables(Unit.GAS_FILLING_STATION)
        save_to_database(filtered_json)
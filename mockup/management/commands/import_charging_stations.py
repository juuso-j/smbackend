import os
import requests
import logging
import json
from datetime import datetime
from django.core.management import BaseCommand
from django import db
from django.contrib.gis.geos import Point, Polygon
from django.contrib.contenttypes.models import ContentType
from mockup.models import Unit, Geometry, ChargingStationContent

logger = logging.getLogger()

CHARGING_STATIONS_URL = "https://services1.arcgis.com/rhs5fjYxdOG1Et61/ArcGIS/rest/services/ChargingStations/FeatureServer/0/query?f=json&where=1%20%3D%201%20OR%201%20%3D%201&returnGeometry=true&spatialRel=esriSpatialRelIntersects&outFields=LOCATION_ID%2CNAME%2CADDRESS%2CURL%2COBJECTID%2CTYPE"
GAS_STATIONS_URL = "https://services1.arcgis.com/rhs5fjYxdOG1Et61/ArcGIS/rest/services/GasFillingStations/FeatureServer/0/query?f=json&where=1%3D1&outFields=OPERATOR%2CLAT%2CLON%2CSTATION_NAME%2CADDRESS%2CCITY%2CZIP_CODE%2CLNG_CNG%2CObjectId"

#GEOMETRY_URL = "https://data.foli.fi/geojson/bounds" # contains the boundries for location filtering
GEOMETRY_ID = 11 #  11 Varsinaissuomi # 10 Uusim
GEOMETRY_URL = "https://tie.digitraffic.fi/api/v3/data/traffic-messages/area-geometries?id={id}&lastUpdated=false"

def fetch_json(url):
    response = requests.get(url)
    assert response.status_code == 200, "Fetching charging stations: {} status code: {}".\
            format(CHARGING_STATIONS_URL, response.status_code)
    return response.json()

def get_filtered_json(json_data):
    geometry_data = fetch_json(GEOMETRY_URL.format(id=GEOMETRY_ID)) 
    polygon = Polygon(geometry_data["features"][0]["geometry"]["coordinates"][0])
    out_data = []
    wkid = json_data["spatialReference"]["wkid"]

    for data in json_data["features"]:
        lon = data["geometry"].get("x",0)
        lat = data["geometry"].get("y",0)
        point = Point(lon, lat)
        if polygon.intersects(point):
            out_data.append(data)
    return wkid, out_data
        
@db.transaction.atomic    
def to_database(json_data, wkid):
    for data in json_data:
        is_active = True
        content_type = Unit.CHARGING_STATION       
        lon = data["geometry"].get("x",0)
        lat = data["geometry"].get("y",0)
        point = Point(lon,lat, srid=wkid)
        attributes = data.get("attributes", None)
        if not attributes:
            continue

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
        # if content_created:
        #     # get with type and id, if exists. add mofiied, else create
        #     unit = Unit.objects.get(content=content)



     
        
        # breakpoint()
        # unit1 = Unit.objects.create(content=content)
        #unit2 = Unit.objects.create(geometry=geometry)
        #unit3, created = Unit.objects.update_or_create(type=0,is_active=True, content_id=content.pk, content_type=ContentType.objects.get_for_model(ChargingStationContent))
        # breakpoint()
        # unit = Unit.objects.get(content=content)
        # breakpoint()

        # unit, created = Unit.objects.update_or_create(
        #     is_active=True, 
        #     geometry=geometry, 
        #     content=content
        # )
          
def delete_tables():
    Unit.objects.filter(content_type=Unit.CHARGING_STATION).delete()
    
class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(            
            "--test-mode",             
            nargs="+",
            default=False,
            help="Run script in test mode. Uses Generated pandas dataframe.",
        )       
    
    def handle(self, *args, **options):
        delete_tables()
        if options["test_mode"]:
            # TODO get current working directory
            f = open(os.getcwd()+"/mockup/tests/"+options["test_mode"], "r")
            json_data = json.load(f)
        else:
            json_data = fetch_json(CHARGING_STATIONS_URL)
        wkid, filtered_json = get_filtered_json(json_data)
        to_database(filtered_json, wkid)
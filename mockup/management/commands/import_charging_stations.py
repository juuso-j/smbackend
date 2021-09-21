import requests
import logging
import json
from django.core.management import BaseCommand
from django import db
from django.contrib.gis.geos import Point, Polygon, geometry
from django.contrib.contenttypes.models import ContentType
from mockup.models import Unit, UNIT_TYPES
from mockup.models import PointGeometry
from mockup.models import ChargingStationContent

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
    for data in json_data["features"]:
        lon = data["geometry"].get("x",0)
        lat = data["geometry"].get("y",0)
        point = Point(lon, lat)
        if polygon.intersects(point):
            out_data.append(data)
    return out_data
        
#@db.transaction.atomic    
def to_database(json_data):
    for data in json_data:
        lon = data["geometry"].get("x",0)
        lat = data["geometry"].get("y",0)
        geometry = PointGeometry.objects.create(geometry=Point(lon,lat))
        attributes = data["attributes"]
        name = attributes.get("NAME", "")
        address = attributes.get("ADDRESS", "")
        url = attributes.get("URL", "")
        charger_type = attributes.get("TYPE", "")
        content = ChargingStationContent.objects.create(
            name=name, 
            address=address,
            url=url,
            charger_type=charger_type
        )
        unit1 = Unit.objects.create(content=content)
        unit2 = Unit.objects.create(geometry=geometry)
        Unit.objects.update_or_create(content_id=content.pk, content_type=ContentType.objects.get_for_model(ChargingStationContent))
        breakpoint()
        unit, created = Unit.objects.update_or_create(
            is_active=True, 
            geometry=geometry, 
            content=content
        )
          
   

class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):
        json_data = fetch_json(CHARGING_STATIONS_URL)
        filtered_json = get_filtered_json(json_data)
        to_database(filtered_json)
import logging
from django.contrib.gis.geos import Point, Polygon
from django import db
from django.conf import settings
from .utils import delete_tables, fetch_json
from data_view.models import (
    MobileUnit,
    ContentTypes,
    ChargingStationContent
    )
logger = logging.getLogger("django")

CHARGING_STATIONS_URL = "https://services1.arcgis.com/rhs5fjYxdOG1Et61/ArcGIS/rest/services/ChargingStations/FeatureServer/0/query?f=json&where=1%20%3D%201%20OR%201%20%3D%201&returnGeometry=true&spatialRel=esriSpatialRelIntersects&outFields=LOCATION_ID%2CNAME%2CADDRESS%2CURL%2COBJECTID%2CTYPE"
GEOMETRY_ID = 11 #  11 Varsinaissuomi # 10 Uusim
GEOMETRY_URL = "https://tie.digitraffic.fi/api/v3/data/traffic-messages/area-geometries?id={id}&lastUpdated=false".format(id=GEOMETRY_ID)

#CHARGING_STATIONS_URL = "https://latauskartta.fi/backend.php?tagFilter=false&idlimit=0&action=getData&editmode=false&chargers_type2=true&chargers_spc=true&chargers_chademo=true&chargers_ccs=true&chargers_hpc=true&chargers_tyomaa=false&unverified=false"

class ChargingStation:

    def __init__(self, elem, srid=settings.DEFAULT_SRID):
        self.is_active = True
        geometry = elem.get("geometry", None)
        attributes = elem.get("attributes", None)      
        # self.srid = srid
        x = geometry.get("x",0)
        y = geometry.get("y",0) 
        self.point = Point(x, y, srid=srid)
        self.name = attributes.get("NAME", "")
        self.address = attributes.get("ADDRESS", "")
        self.url = attributes.get("URL", "")
        self.charger_type = attributes.get("TYPE", "")        
    
    def __init__OLD(self, elem, srid=settings.DEFAULT_SRID):
        self.is_active = True
     
        geometry = elem.get("geometry", None)
        attributes = elem.get("attributes", None)      
        x = geometry.get("x",0)
        y = geometry.get("y",0)     
        self.point(x, y, srid=srid) 
     
        self.x = geometry.get("x",0)
        self.y = geometry.get("y",0)      
        self.name = attributes.get("NAME", "")
        self.address = attributes.get("ADDRESS", "")
        self.url = attributes.get("URL", "")
        self.charger_type = attributes.get("TYPE", "")           


def build_and_filter_objects_from_locations(locations):

    for index in locations.keys():
        location = locations[index]
        breakpoint()


def get_filtered_charging_station_objects_TODO(): 
    json_data = fetch_json(CHARGING_STATIONS_URL)
    locations = json_data["locations"]
   
    breakpoint()

def get_filtered_charging_station_objects(): 
    """
    Returns a list of ChargingStation objects that are filtered by location.
    """   
    geometry_data = fetch_json(GEOMETRY_URL) 
    # Polygon used the detect if point intersects. i.e. is in the boundries.
    polygon = Polygon(geometry_data["features"][0]["geometry"]["coordinates"][0])  
    json_data = fetch_json(CHARGING_STATIONS_URL)
    srid = json_data["spatialReference"]["wkid"]
    objects = [ChargingStation(data, srid=srid) for data in json_data["features"]]
    filtered_objects = []
    # Filter objects
    for object in objects:    
        #point = Point(object.x, object.y)        
        if polygon.intersects(object.point):
            filtered_objects.append(object)
    logger.info("Filtered: {} charging stations by location to: {}."\
        .format(len(json_data["features"]), len(filtered_objects)))        
    return filtered_objects


@db.transaction.atomic    
def save_to_database(objects, delete_table=True):
    if delete_table:
        delete_tables(ContentTypes.CHARGING_STATION)
    description = "Charging stations in province of SouthWest Finland."
    content_type = ContentTypes.objects.get_or_create(
        type_name=ContentTypes.CHARGING_STATION,
        name="Charging Station",
        class_name=ContentTypes.CONTENT_TYPES[ContentTypes.CHARGING_STATION],
        description=description
    )[0]

    for object in objects:
        is_active = object.is_active 
        # x = object.x
        # y = object.y      
        #point = Point(x,y, srid=object.srid) 
        point = object.point
        #point.transform(settings.DEFAULT_SRID)  
        name = object.name
        address = object.address
        url = object.url
        charger_type = object.charger_type  
        mobile_unit = MobileUnit.objects.create(
            is_active=is_active,
            name=name,
            address=address,
            geometry=point,
            content_type=content_type
        )
        content = ChargingStationContent.objects.create(
            mobile_unit=mobile_unit,
            url=url,
            charger_type=charger_type
        )
       
    logger.info("Saved charging stations to database.")
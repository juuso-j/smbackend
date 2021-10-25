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


class ChargingStation:

    def __init__(self, elem, srid=settings.DEFAULT_SRID):
        self.is_active = True
        self.srid=srid       
        geometry = elem.get("geometry", None)
        attributes = elem.get("attributes", None)      
        self.x = geometry.get("x",0)
        self.y = geometry.get("y",0)      
        self.name = attributes.get("NAME", "")
        self.address = attributes.get("ADDRESS", "")
        self.url = attributes.get("URL", "")
        self.charger_type = attributes.get("TYPE", "")        
       

# def get_json_filtered_by_location(json_data):
#     geometry_data = fetch_json(GEOMETRY_URL) 
#     polygon = Polygon(geometry_data["features"][0]["geometry"]["coordinates"][0])
#     filtered_data = []
#     srid = json_data["spatialReference"]["wkid"]
#     for data in json_data["features"]:
#         x = data["geometry"].get("x",0)
#         y = data["geometry"].get("y",0)
#         point = Point(x, y)
#         if polygon.intersects(point):
#             obj = ChargingStation(data, srid)
#             filtered_data.append(obj)
#     logger.info("Filtered: {} charging stations by location to: {}."\
#         .format(len(json_data["features"]), len(filtered_data)))
        
#     return filtered_data

def get_filtered_charging_station_objects(): 
    """
    Returns a list of ChargingStation objects that are filtered by location.
    """   
    geometry_data = fetch_json(GEOMETRY_URL) 
    # Polygon used the detect if point intersects. i.e. is in the boundries.
    polygon = Polygon(geometry_data["features"][0]["geometry"]["coordinates"][0])  
    json_data = fetch_json(CHARGING_STATIONS_URL)
    srid = json_data["spatialReference"]["wkid"]
    objects = [ChargingStation(data, srid) for data in json_data["features"]]
    filtered_objects = []
    # Filter objects
    for object in objects:
        point = Point(object.x, object.y)        
        if polygon.intersects(point):
            filtered_objects.append(object)
    logger.info("Filtered: {} gas filling stations by location to: {}."\
        .format(len(json_data["features"]), len(filtered_objects)))        
    return filtered_objects


@db.transaction.atomic    
def save_to_database(objs, delete_table=True):
    if delete_table:
        delete_tables(ContentTypes.CHARGING_STATION)
    description = "Charging stations in province of SouthWest Finland."
    content_type = ContentTypes.objects.get_or_create(
        type_name=ContentTypes.CHARGING_STATION,
        name="Charging Station",
        class_name=ContentTypes.CONTENT_TYPES[ContentTypes.CHARGING_STATION],
        description=description
    )[0]

    for obj in objs:
        is_active = obj.is_active     
        x = obj.x
        y = obj.y         
        point = Point(x,y, srid=obj.srid) 
        point.transform(settings.DEFAULT_SRID)    
        name = obj.name
        address = obj.address
        url = obj.url
        charger_type = obj.charger_type  
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
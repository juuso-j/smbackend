import logging
from django.contrib.gis.geos import GEOSGeometry, Point, Polygon
from django import db
from django.conf import settings
from data_view.models import (
    MobileUnit, 
    ContentTypes, 
    GasFillingStationContent
)
from .utils import fetch_json, delete_tables, GEOMETRY_URL
logger = logging.getLogger("django")
GAS_FILLING_STATIONS_URL = "https://services1.arcgis.com/rhs5fjYxdOG1Et61/ArcGIS/rest/services/GasFillingStations/FeatureServer/0/query?f=json&where=1%3D1&outFields=OPERATOR%2CLAT%2CLON%2CSTATION_NAME%2CADDRESS%2CCITY%2CZIP_CODE%2CLNG_CNG%2CObjectId"


class GasFillingStation:

    def __init__(self, elem, srid=settings.DEFAULT_SRID):
        self.is_active = True
        attributes = elem.get("attributes")        
        #self.srid = srid
        x = attributes.get("LON",0)
        y = attributes.get("LAT",0)
        self.point = Point(x, y, srid=srid)              
        self.name = attributes.get("STATION_NAME", "")
        self.address =attributes.get("ADDRESS", "")        
        self.zip_code = attributes.get("ZIP_CODE", "")
        self.city = attributes.get("CITY", "")      
        self.operator = attributes.get("OPERATOR", "")
        self.lng_cng = attributes.get("LNG_CNG", "") 
        # address fields for service unit model
        self.street_address = self.address.split(",")[0]        
        self.address_postal_full = "{} {} {}"\
            .format(self.address, self.zip_code, self.city)

def get_filtered_gas_filling_station_objects(): 
    """
    Returns a list of GasFillingStation objects that are filtered by location.
    """   
    geometry_data = fetch_json(GEOMETRY_URL) 
    # Polygon used the detect if point intersects. i.e. is in the boundries.
    polygon = Polygon(geometry_data["features"][0]["geometry"]["coordinates"][0])  
    json_data = fetch_json(GAS_FILLING_STATIONS_URL)
    #srid = json_data["spatialReference"]["wkid"]
    # NOTE, hack to fix srid 102100 causes "crs not found"
    srid = 4326
    # Create list of GasFillingStation objects
    objects = [GasFillingStation(data, srid=srid) for data in json_data["features"]]
    filtered_objects = []
    # Filter objects
    for object in objects:
        #point = Point(object.x, object.y)        
        if polygon.intersects(object.point):
            filtered_objects.append(object)
    logger.info("Filtered: {} gas filling stations by location to: {}."\
        .format(len(json_data["features"]), len(filtered_objects)))        
    return filtered_objects
   


# def get_json_filtered_by_location(json_data):
#     geometry_data = fetch_json(GEOMETRY_URL) 
#     polygon = Polygon(geometry_data["features"][0]["geometry"]["coordinates"][0])
#     filtered_data = []
#     #srid = json_data["spatialReference"]["wkid"]
#     # NOTE, hack to fix srid 102100 causes "crs not found"
#     srid = 3857    

#     for data in json_data["features"]:
#         lon = data["attributes"].get("LON",0)
#         lat = data["attributes"].get("LAT",0)
#         point = Point(lon, lat)
#         if polygon.intersects(point):
#             object = GasFillingStation(data, srid)
#             filtered_data.append(object)
#     logger.info("Filtered: {} gas filling stations by location to: {}."\
#         .format(len(json_data["features"]), len(filtered_data)))
#     return filtered_data


@db.transaction.atomic  
def save_to_database(objects, delete_table=True):
    if delete_table:
        delete_tables(ContentTypes.GAS_FILLING_STATION)        
    description = "Gas filling stations in province of SouthWest Finland."
    # Create contet_type ins

    content_type = ContentTypes.objects.get_or_create(
        type_name=ContentTypes.GAS_FILLING_STATION,
        name="Gas Filling Station",
        class_name=ContentTypes.CONTENT_TYPES[ContentTypes.GAS_FILLING_STATION],
        description=description
    )[0]
    for object in objects:
        is_active = object.is_active      
        # x = object.x
        # y = object.y      
        # point = Point(x,y, srid=object.srid) 
        # point.transform(settings.DEFAULT_SRID)  
        point = object.point
        name = object.name
        address = object.address
        #zip_code = object.zip_code
        #city = object.city
        address += ", " + object.zip_code + " " + object.city
        operator = object.operator
        lng_cng = object.lng_cng 
        mobile_unit = MobileUnit.objects.create(
            is_active=is_active,
            name=name,
            address=address,
            geometry=point,
            content_type=content_type
        )
        content = GasFillingStationContent.objects.create(
            mobile_unit=mobile_unit,
            operator=operator,
            lng_cng=lng_cng
        )        

    logger.info("Saved gas filling stations to database.")

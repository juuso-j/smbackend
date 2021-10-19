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
        self.srid = srid
        attributes = elem.get("attributes")
        self.x = attributes.get("LON",0)
        self.y = attributes.get("LAT",0)               
        self.name = attributes.get("STATION_NAME", "")
        self.address = attributes.get("ADDRESS", "")
        self.zip_code = attributes.get("ZIP_CODE", "")
        self.city = attributes.get("CITY", "")
        self.address += ", " + self.zip_code + " " + self.city
        self.operator = attributes.get("OPERATOR", "")
        self.lng_cng = attributes.get("LNG_CNG", "") 
        # class GasFillingStationImporter:

#     def __init__(self, logger=None, importer=None, test=False):
#         self.logger = logger
#         self.importer = importer
#         self.test = test    
    
    
#     def import_gas_filling_stations(self):
#         json_data = fetch_json(GAS_FILLING_STATIONS_URL)
#         srid, filtered_json = self.get_json_filtered_by_location(json_data)
#         delete_tables(ContentTypes.GAS_FILLING_STATION)
#         self.save_to_database(filtered_json, srid)


def get_json_filtered_by_location(json_data):
    geometry_data = fetch_json(GEOMETRY_URL) 
    polygon = Polygon(geometry_data["features"][0]["geometry"]["coordinates"][0])
    filtered_data = []
    #srid = json_data["spatialReference"]["wkid"]
    # NOTE, hack to fix srid 102100 causes "crs not found"
    srid = 3857    

    for data in json_data["features"]:
        lon = data["attributes"].get("LON",0)
        lat = data["attributes"].get("LAT",0)
        point = Point(lon, lat)
        if polygon.intersects(point):
            obj = GasFillingStation(data, srid)
            filtered_data.append(obj)
    logger.info("Filtered: {} gas filling stations by location to: {}."\
        .format(len(json_data["features"]), len(filtered_data)))
    return filtered_data

@db.transaction.atomic  
def save_to_database(objs, delete_table=True):
    if delete_table:
        delete_tables(ContentTypes.GAS_FILLING_STATION)
        
    description = "Gas filling stations in province of SouthWest Finland."
    content_type = ContentTypes.objects.get_or_create(
        type_name=ContentTypes.GAS_FILLING_STATION,
        name="Gas Filling Station",
        class_name=ContentTypes.CONTENT_TYPES[ContentTypes.GAS_FILLING_STATION],
        description=description
    )[0]
    for obj in objs:
        is_active = obj.is_active
        #content_type_name = Unit.GAS_FILLING_STATION 
        # attributes = data.get("attributes", None)
        # geometry = data.get("geometry", None)
        # if not attributes or not geometry:
        #     continue

        x = obj.x
        y = obj.y 
        point = Point(x,y,srid=obj.srid)
        point.transform(settings.DEFAULT_SRID)
        name = obj.name
        address = obj.address
        zip_code = obj.zip_code
        city = obj.city
        address += ", " + obj.zip_code + " " + obj.city
        operator = obj.operator
        lng_cng = obj.lng_cng 
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

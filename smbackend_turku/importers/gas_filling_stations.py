import requests
import logging
from enum import Enum
from django.contrib.gis.geos import Point, Polygon
from .utils import fetch_json, ServiceCodes
logger = logging.getLogger("django")


GEOMETRY_ID = 11 #  11 Varsinaissuomi # 10 Uusim
GAS_FILLING_STATIONS_URL = "https://services1.arcgis.com/rhs5fjYxdOG1Et61/ArcGIS/rest/services/GasFillingStations/FeatureServer/0/query?f=json&where=1%3D1&outFields=OPERATOR%2CLAT%2CLON%2CSTATION_NAME%2CADDRESS%2CCITY%2CZIP_CODE%2CLNG_CNG%2CObjectId"

GEOMETRY_URL = "https://tie.digitraffic.fi/api/v3/data/traffic-messages/area-geometries?id={id}&lastUpdated=false".format(id=GEOMETRY_ID)

def get_json_filtered_by_location():
    json_data = fetch_json(GAS_FILLING_STATIONS_URL)
    geometry_data = fetch_json(GEOMETRY_URL) 
    polygon = Polygon(geometry_data["features"][0]["geometry"]["coordinates"][0])
    filtered_data = []
    #srid = json_data["spatialReference"]["wkid"]
    for data in json_data["features"]:
        lon = data["attributes"].get("LON",0)
        lat = data["attributes"].get("LAT",0)
        point = Point(lon, lat)
        if polygon.intersects(point):
            filtered_data.append(data)
    logger.info("Filtered: {} gas filling stations by location to: {}."\
        .format(len(json_data["features"]), len(filtered_data)))
    return filtered_data


def get_gas_filling_station_units(koodi):

    filtered_data = get_json_filtered_by_location()
    out_data = []
    for i, elem in enumerate(filtered_data):
        unit = {}
        attributes = elem.get("attributes")
        x = attributes.get("LON",0)
        y = attributes.get("LAT",0)               
        name = attributes.get("STATION_NAME", "")
        address = attributes.get("ADDRESS", "")
        zip_code = attributes.get("ZIP_CODE", "")
        city = attributes.get("CITY", "")
        address += ", " + zip_code + " " + city
        operator = attributes.get("OPERATOR", "")
        lng_cng = attributes.get("LNG_CNG", "") 
        unit["koodi"] = str(koodi+i)
        unit["nimi_kieliversiot"] = {}        
        unit["nimi_kieliversiot"]["fi"] = name
        unit["fyysinenPaikka"] = {}
        unit["fyysinenPaikka"]["leveysaste"] = y; 
        unit["fyysinenPaikka"]["pituusaste"] = x; 
        unit["fyysinenPaikka"]["koordinaattiAsettuKasin"] = "True"
        unit["tila"] = {}
        unit["tila"]["koodi"] = "1"
        unit["tila"]["nimi"] = "Aktiivinen, julkaistu"
        unit["kuvaus_kieliversiot"] = {}
        unit["kuvaus_kieliversiot"]["fi"] = operator + " " + lng_cng         
        unit["palvelutarjoukset"] = []
        extra = {}
        extra["operator"] = operator
        extra["lng_cng"] = lng_cng
        unit["extra"] = extra
        palvelut = {}
        palvelut["palvelut"] = []
        palvelu = {}
        palvelu["koodi"] = "9999"
        palvelut["palvelut"].append(palvelu)
        unit["palvelutarjoukset"].append(palvelut)
        out_data.append(unit)

    return out_data


def get_gas_filling_station_service_node(
    ylatason_koodi="1_35",
    koodi="1_99", # WHAT?    
    services=[]
    ):
    
    service_node = {}
    service_node["ylatason_koodi"] = ylatason_koodi
    service_node["koodi"] = koodi
    service_node["nimi_kieliversiot"] = {}
    service_node["nimi_kieliversiot"]["fi"] = "Kaasun tankkausasemat"
    service_node["nimi_kieliversiot"]["sv"] = "Gas stationer"
    service_node["nimi_kieliversiot"]["en"] = "Gas filling stations"

    service_node["luokittelutyyppi"] = {}
    service_node["luokittelutyyppi"]["koodi"] = "1"
    service_node["luokittelutyyppi"]["nimi"] = "JHS-183"
    service_node["palvelut"] = []
    palvelu = {}
    palvelu["koodi"] = ServiceCodes.GAS_FILLING_STATION # JHS-183 tunnus?
    service_node["palvelut"].append(palvelu)
    return [service_node]

def get_gas_filling_station_service():
    service = {}
    service["koodi"] = ServiceCodes.GAS_FILLING_STATION
    service["tila"] = {}
    service["tila"]["koodi"] = "1"
    service["tila"]["nimi"] = "Aktiivinen, julkaistu"
    service["nimi_kieliversiot"] = {}
    service["nimi_kieliversiot"]["fi"] = "Kaasun latauspiste"
    return [service]

   



import logging

from django.conf import settings
#from django.contrib.gis.geos import Point, Polygon
#from django import db

from .utils import fetch_json, ServiceCodes
#from data_view.importers.utils import fetch_json
from data_view.importers.gas_filling_station import (
    get_json_filtered_by_location,
    save_to_database,
    GAS_FILLING_STATIONS_URL,
)
logger = logging.getLogger("django")


# GEOMETRY_ID = 11 #  11 Varsinaissuomi # 10 Uusim
# GAS_FILLING_STATIONS_URL = "https://services1.arcgis.com/rhs5fjYxdOG1Et61/ArcGIS/rest/services/GasFillingStations/FeatureServer/0/query?f=json&where=1%3D1&outFields=OPERATOR%2CLAT%2CLON%2CSTATION_NAME%2CADDRESS%2CCITY%2CZIP_CODE%2CLNG_CNG%2CObjectId"

# GEOMETRY_URL = "https://tie.digitraffic.fi/api/v3/data/traffic-messages/area-geometries?id={id}&lastUpdated=false".format(id=GEOMETRY_ID)
#CONTENT_TYPE = "GasFillingStation"


# @db.transaction.atomic    
# def to_database(json_data):

#     # copy code...
#     # SOLVE, howto get the unit_id = KOODI
#     # only the code.
#     pass
# class GasFillingStationImporter:

#     def __init__(self, logger=None, importer=None, test=False):
#         self.logger = logger
#         self.importer = importer
#         self.test = test


def get_gas_filling_station_units(koodi, to_database=False):
    json_data = fetch_json(GAS_FILLING_STATIONS_URL)
    filtered_data = get_json_filtered_by_location(json_data)
    if to_database:
        save_to_database(filtered_data)

    out_data = []
    for i, obj in enumerate(filtered_data):
        unit = {}     
        address = obj.address + ", " + obj.zip_code + " " + obj.city        
        unit["koodi"] = str(koodi+i)
        unit["nimi_kieliversiot"] = {}        
        unit["nimi_kieliversiot"]["fi"] = obj.name
        unit["fyysinenPaikka"] = {}
        unit["fyysinenPaikka"]["leveysaste"] = obj.y; 
        unit["fyysinenPaikka"]["pituusaste"] = obj.x; 
        unit["fyysinenPaikka"]["koordinaattiAsettuKasin"] = "True"
        unit["fyysinenPaikka"]["osoitteet"] = []
        osoite = {}
        osoite["katuosoite_fi"] = address
        osoite["katuosoite_sv"] = address
        osoite["katuosoite_en"] = address
        osoite["postinumero"] = obj.zip_code
        osoite["postitoimipaikka_fi"] = obj.city
        osoite["postitoimipaikka_sv"] = obj.city
        osoite["postitoimipaikka_en"] = obj.city
        unit["fyysinenPaikka"]["osoitteet"].append(osoite)
        unit["tila"] = {}
        unit["tila"]["koodi"] = "1" # must be 1, to be visible.
        unit["tila"]["nimi"] = "Aktiivinen, julkaistu"
        unit["kuvaus_kieliversiot"] = {}
        unit["kuvaus_kieliversiot"]["fi"] = obj.operator + " " + obj.lng_cng         
        unit["kuvaus_kieliversiot"]["sv"] = obj.operator + " " + obj.lng_cng         
        unit["kuvaus_kieliversiot"]["en"] = obj.operator + " " + obj.lng_cng         

        
        extra = {}       
        extra["operator"] = obj.operator
        extra["lng_cng"] = obj.lng_cng
        unit["extra"] = extra
        # Palvelut
        unit["palvelutarjoukset"] = []
        palvelut = {}
        palvelut["palvelut"] = []
        palvelu = {}
        palvelu["koodi"] = ServiceCodes.GAS_FILLING_STATION
        palvelut["palvelut"].append(palvelu)
        unit["palvelutarjoukset"].append(palvelut)
        out_data.append(unit)
    return out_data


def get_gas_filling_station_service_node(        
    ylatason_koodi="1_35", # Vapaa aika
    koodi="1_99", # WHAT?    
    services=[]
    ):    
    service_node = {}
    service_node["ylatason_koodi"] = ylatason_koodi
    service_node["koodi"] = koodi
    service_node["nimi_kieliversiot"] = {}
    service_node["nimi_kieliversiot"]["fi"] = "Kaasutankkausasemat"
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
    service["nimi_kieliversiot"]["fi"] = "Kaasuntankkausema"
    return [service]


# def import_gas_filling_stations(**kwargs):
#     print(kwargs)
#     importer = GasFillingStationImporter(**kwargs)
#     return importer.get_gas_filling_station_units()
   

from munigeo.importer.sync import ModelSyncher
from services.models import (
    Service,
    ServiceNode,
    Unit,
    UnitAccessibilityShortcomings,
    UnitConnection,
    UnitIdentifier,
    UnitServiceDetails,
)

ROOT_FIELD_MAPPING = {
    "nimi_kieliversiot": "name",
    "kuvaus_kieliversiot": "description",
    "sahkoposti": "email",
}
from smbackend_turku.importers.utils import (
    convert_code_to_int,
    get_turku_resource,
    set_syncher_object_field,
    set_syncher_tku_translated_field,
)
from smbackend_turku.importers.utils import (
    get_localized_value,
    get_turku_resource,
    get_weekday_str,
    set_syncher_object_field,
    set_syncher_tku_translated_field,
)
from django.contrib.gis.geos import Point, Polygon
from django.conf import settings
from datetime import date, datetime
import pytz

UTC_TIMEZONE = pytz.timezone("UTC")
SOURCE_DATA_SRID = 4326
SERVICE_NODE_ID = 10001
def import_gas():
    unitsyncher = ModelSyncher(Unit.objects.all(), lambda obj: obj.id)

    json_data = fetch_json(GAS_FILLING_STATIONS_URL)
    filtered_data = get_json_filtered_by_location(json_data)
    id_off =  Unit.objects.all().order_by("-id")[0].id+1
    for i, data_obj in enumerate(filtered_data):
        unit_id = i + id_off
        obj = unitsyncher.get(unit_id)
        if not obj:
            obj = Unit(id=unit_id)
            obj._changed = True
        point = Point(data_obj.x, data_obj.y, srid=SOURCE_DATA_SRID)
        set_syncher_object_field(obj, "location", point)    
        set_syncher_object_field(obj, "name", data_obj.name)
        set_syncher_object_field(obj, "street_address", data_obj.address)

        service_id = "4242"
        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            # TODO fail the unit node completely here?
            logger.warning(
                'Service "{}" does not exist!'.format(service_id)
            )
            continue
        UnitServiceDetails.objects.get_or_create(unit=obj, service=service)

        service_nodes = ServiceNode.objects.filter(related_services=service)
        obj.service_nodes.add(*service_nodes)
        if obj._changed:
            obj.last_modified_time = datetime.now(UTC_TIMEZONE)
            obj.save()
    
        unitsyncher.mark(obj)

    #breakpoint()


def import_gas_service_node():
    nodesyncher = ModelSyncher(ServiceNode.objects.all(), lambda obj: obj.id)
    node_id = SERVICE_NODE_ID
    obj = nodesyncher.get(node_id)

    if not obj:
        obj = ServiceNode(id=node_id)
        obj._changed = True

    name = "TestiKaasu"
    ylatason_koodi = "1_35"
    set_syncher_object_field(obj, "name", name)
    set_syncher_object_field(obj, "name_fi", name)
    parent_id = convert_code_to_int(ylatason_koodi)
    parent = nodesyncher.get(parent_id)
    if obj.parent != parent:
        obj.parent = parent
        obj._changed = True

    if obj._changed:
        obj.last_modified_time = datetime.now(UTC_TIMEZONE)
        obj.save()
    #nodesyncher.finish()
    

def import_gas_service():
    # TODO add filter to get gas stations.
    servicesyncher = ModelSyncher(Service.objects.all(), lambda obj: obj.id)
    koodi = 4242
    obj = servicesyncher.get(koodi)
    if not obj:
        obj = Service(id=koodi, clarification_enabled=False, period_enabled=False)
        obj._changed = True

    set_syncher_object_field(obj, "name", "Testikaasu service")
    if obj._changed:
        print("saving testi kaasu asema")
        obj.last_modified_time = datetime.now(UTC_TIMEZONE)
        obj.save()

    service_node = ServiceNode(id=SERVICE_NODE_ID)
    #breakpoint()
    service_node.related_services.add(koodi)

if __name__ == "__main__":

    import_gas()
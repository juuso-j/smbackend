from datetime import datetime
import pytz
from functools import lru_cache

from django.contrib.gis.geos import Point
from django.conf import settings
from data_view.importers.gas_filling_station import (
    get_filtered_gas_filling_station_objects  
)

from data_view.importers.charging_stations import(
   get_filtered_charging_station_objects
)
from munigeo.importer.sync import ModelSyncher
from munigeo.models import Municipality

from services.management.commands.services_import.services import (
    update_service_node_counts,  
)   
from smbackend_turku.importers.utils import (

    fetch_json, # TODO, move to stations_utils
    set_syncher_object_field,
    set_syncher_tku_translated_field,
)
from services.models import (
    Service,
    ServiceNode,
    Unit,   
    UnitServiceDetails,
)

from smbackend_turku.importers.utils import (  
    set_syncher_object_field,
    set_syncher_tku_translated_field,
)



UTC_TIMEZONE = pytz.timezone("UTC")
LANGUAGES = [language[0] for language in settings.LANGUAGES]

SOURCE_DATA_SRID = 4326

@lru_cache(None)
def get_municipality(name):
    try:
        return Municipality.objects.get(name=name)
    except Municipality.DoesNotExist:
        return None

def save_object(obj):
    if obj._changed:
        obj.last_modified_time = datetime.now(UTC_TIMEZONE)
        obj.save()

def create_language_dict(value):
    lang_dict = {}
    for lang in LANGUAGES:
        lang_dict[lang] = value
    return lang_dict

def get_serivice_node_id(name):
    service_node = None
    service_node_id = None
    try:
        service_node = ServiceNode.objects.get(name=name)
    except ServiceNode.DoesNotExist:    
        print("Service Node does not exist")   
        # Highest available id
        service_node_id = ServiceNode.objects.all().order_by("-id")[0].id+1
    else:
        print("Service nodeexists")
        service_node_id = service_node.id
    return service_node_id 


def generate_service_node(service_node_id, parent_name, service_node_names):
    nodesyncher = ModelSyncher(ServiceNode.objects.all(), lambda obj: obj.id)    
    obj = nodesyncher.get(service_node_id)
    if not obj:
        obj = ServiceNode(id=service_node_id)
        obj._changed = True

    parent_id = ServiceNode.objects.get(name=parent_name).id
    parent = nodesyncher.get(parent_id)
    if obj.parent != parent:
        obj.parent = parent
        obj._changed = True
    set_syncher_tku_translated_field(obj, "name", service_node_names)
    save_object(obj)
                
def generate_service(service_node_id, service_name, service_names):
    servicesyncher = ModelSyncher(
        Service.objects.filter(name=service_name), 
        lambda obj: obj.id
        )

    service = None
    try:
        service = Service.objects.get(name=service_name)
    except Service.DoesNotExist:    
        print("srevice does not exist")   
        # Highest available id
        service_id = Service.objects.all().order_by("-id")[0].id+1
    else:
        print("exists")
        service_id = service.id

    obj = servicesyncher.get(service_id)
    if not obj:
        obj = Service(id=service_id, clarification_enabled=False, period_enabled=False)
        obj._changed = True

    set_syncher_tku_translated_field(obj, "name", service_names)     
    service_node = ServiceNode(id=service_node_id)
    service_node.related_services.add(service_id)
    save_object(obj)
    # TODO, why finish destroys the service?
    #servicesyncher.finish()
    return service_id

class GasFillingStationImporter:

    SERVICE_NODE_NAMES = {
        "fi": "Kaasutankkausasemat",
        "sv": "Gas stationer",
        "en": "Gas filling stations"
    }
    SERVICE_NAMES = {
        "fi": "Kaasutankkausasema",
        "sv": "Gas station",
        "en": "Gas filling station"
    }
    def __init__(self, logger=None, importer=None, test=False):
        self.logger = logger
        self.importer = importer
        self.test = test   

    def import_gas_filling_stations(self, service_id):
        unitsyncher = ModelSyncher(Unit.objects.filter(services__id=service_id), lambda obj: obj.id)
        filtered_objects = get_filtered_gas_filling_station_objects()
        # Find the highest unit id and add 1. This ensures that we get unique id:s
        id_off =  Unit.objects.all().order_by("-id")[0].id+1
        for i, data_obj in enumerate(filtered_objects):
            unit_id = i + id_off
            obj = unitsyncher.get(unit_id)
            if not obj:
                obj = Unit(id=unit_id)
                obj._changed = True
            point = Point(data_obj.x, data_obj.y, srid=SOURCE_DATA_SRID)
            set_syncher_object_field(obj, "location", point)    
            set_syncher_tku_translated_field(obj, "name",\
                create_language_dict(data_obj.name))
            set_syncher_tku_translated_field(obj, "street_address",\
                create_language_dict(data_obj.street_address))
            set_syncher_tku_translated_field(obj, "address_postal_full",\
                create_language_dict(data_obj.address_postal_full))
            set_syncher_object_field(obj, "address_zip", data_obj.zip_code)  
         
            description = "{} {}".format(data_obj.operator, data_obj.lng_cng)            
            set_syncher_tku_translated_field(obj, "description",\
                create_language_dict(description))
            extra = {}
            extra["operator"] = data_obj.operator
            extra["lng_cng"] = data_obj.lng_cng
            set_syncher_object_field(obj, "extra", extra) 
            try:
                service = Service.objects.get(id=service_id)
            except Service.DoesNotExist:
                self.logger.warning(
                    'Service "{}" does not exist!'.format(service_id)
                )
                continue
            UnitServiceDetails.objects.get_or_create(unit=obj, service=service)
            service_nodes = ServiceNode.objects.filter(related_services=service)
            obj.service_nodes.add(*service_nodes)            
            set_syncher_object_field(obj, "root_service_nodes", obj.get_root_service_nodes()[0])
            municipality = get_municipality(data_obj.city)
            set_syncher_object_field(obj, "municipality", municipality)            
            save_object(obj)
        unitsyncher.finish()
        update_service_node_counts()
  

class ChargingStationImporter():
    SERVICE_NODE_NAMES = {
        "fi": "Sähkölatausasemat",
        "sv": "Laddplatser",
        "en": "Charging stations"
    }
    SERVICE_NAMES = {
        "fi": "Sähkölatausasema",
        "sv": "Laddplats",
        "en": "Charging station"
    }
    def __init__(self, logger=None, importer=None, test=False):
        self.logger = logger
        self.importer = importer
        self.test = test 

    def import_charging_stations(self, service_id):
        unitsyncher = ModelSyncher(Unit.objects.filter(services__id=service_id), lambda obj: obj.id)

        filtered_objects = get_filtered_gas_filling_station_objects()
        # Find the highest unit id and add 1. This ensures that we get unique id:s
        
        id_off =  Unit.objects.all().order_by("-id")[0].id+1
        for i, data_obj in enumerate(filtered_objects):
            unit_id = i + id_off
            obj = unitsyncher.get(unit_id)
            if not obj:
                obj = Unit(id=unit_id)
                obj._changed = True
            point = Point(data_obj.x, data_obj.y, srid=SOURCE_DATA_SRID)
            set_syncher_object_field(obj, "location", point)    
            set_syncher_tku_translated_field(obj, "name",\
                create_language_dict(data_obj.name))
      
            breakpoint()
       
    
def import_gas_filling_stations(**kwargs):
    importer = GasFillingStationImporter(**kwargs)  
    service_node_id = get_serivice_node_id(importer.SERVICE_NODE_NAMES["fi"]) 
    service_id = generate_service(service_node_id,\
        importer.SERVICE_NAMES["fi"], importer.SERVICE_NAMES)
    generate_service_node(service_node_id, "Vapaa-aika", importer.SERVICE_NODE_NAMES)
    importer.import_gas_filling_stations(service_id)

def import_charging_stations(**kwargs):
    importer = ChargingStationImporter(**kwargs)  
    service_node_id = get_serivice_node_id(importer.SERVICE_NODE_NAMES["fi"]) 
    service_id = generate_service(service_node_id,\
        importer.SERVICE_NAMES["fi"], importer.SERVICE_NAMES)
    generate_service_node(service_node_id, "Vapaa-aika", importer.SERVICE_NODE_NAMES)
    importer.import_gas_filling_stations(service_id)

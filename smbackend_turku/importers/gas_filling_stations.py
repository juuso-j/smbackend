from datetime import date, datetime
import pytz
from functools import lru_cache

from django.contrib.gis.geos import Point
from django.conf import settings
from data_view.importers.gas_filling_station import (
    get_json_filtered_by_location,
    save_to_database,
    GAS_FILLING_STATIONS_URL,
)
from munigeo.importer.sync import ModelSyncher
from munigeo.models import Municipality

from services.management.commands.services_import.services import (
    update_service_node_counts,  
)   
from smbackend_turku.importers.utils import (

    fetch_json,
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
LANGUAGES = ["fi", "sv", "en"]

SOURCE_DATA_SRID = 4326
SERVICE_NODE_ID = 10001

@lru_cache(None)
def get_municipality(name):
    try:
        return Municipality.objects.get(name=name)
    except Municipality.DoesNotExist:
        return None

class GasFillingStationImporter:

    def __init__(self, logger=None, importer=None, test=False):
        self.logger = logger
        self.importer = importer
        self.test = test   

    def import_gas_filling_stations(self, service_id):
        unitsyncher = ModelSyncher(Unit.objects.filter(services__id=service_id), lambda obj: obj.id)

        json_data = fetch_json(GAS_FILLING_STATIONS_URL)
        filtered_data = get_json_filtered_by_location(json_data)
        # Find the highest unit id. 
        id_off =  Unit.objects.all().order_by("-id")[0].id+1
        for i, data_obj in enumerate(filtered_data):
            unit_id = i + id_off
            obj = unitsyncher.get(unit_id)
            if not obj:
                obj = Unit(id=unit_id)
                obj._changed = True
            point = Point(data_obj.x, data_obj.y, srid=SOURCE_DATA_SRID)
            set_syncher_object_field(obj, "location", point)    
            set_syncher_tku_translated_field(obj, "name",\
                self._create_language_dict(data_obj.name))
            set_syncher_tku_translated_field(obj, "street_address",\
                self._create_language_dict(data_obj.street_address))
            set_syncher_tku_translated_field(obj, "address_postal_full",\
                self._create_language_dict(data_obj.address_postal_full))
            set_syncher_object_field(obj, "address_zip", data_obj.zip_code)  
         
            description = "{} {}".format(data_obj.operator, data_obj.lng_cng)            
            set_syncher_tku_translated_field(obj, "description",\
                self._create_language_dict(description))
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
            self._save_object(obj)
        unitsyncher.finish()
        update_service_node_counts()

    SERVICE_NODE_NAMES = {
        "fi": "Kaasutankkausasemat",
        "sv": "Gas stationer",
        "en": "Gas filling stations"
    }
    # TODO generic,  parent_name, names. 
    def generate_gas_filling_station_service_node(self, service_node_id):
        nodesyncher = ModelSyncher(ServiceNode.objects.all(), lambda obj: obj.id)
        
        obj = nodesyncher.get(service_node_id)

        if not obj:
            obj = ServiceNode(id=service_node_id)
            obj._changed = True
    
        parent_id = ServiceNode.objects.get(name="Vapaa-aika").id
        parent = nodesyncher.get(parent_id)
        if obj.parent != parent:
            obj.parent = parent
            obj._changed = True
        set_syncher_tku_translated_field(obj, "name", self.SERVICE_NODE_NAMES)
        self._save_object(obj)
     
     
    SERVICE_NAMES = {
        "fi": "Kaasutankkausasema",
        "sv": "Gas station",
        "en": "Gas filling station"
    }
    def generate_gas_filling_station_service(self, service_node_id):
        servicesyncher = ModelSyncher(
            Service.objects.filter(name=self.SERVICE_NAMES["fi"]), 
            lambda obj: obj.id
            )
    
        service = None
        try:
            service = Service.objects.get(name=self.SERVICE_NAMES["fi"])
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

        set_syncher_tku_translated_field(obj, "name", self.SERVICE_NAMES)      

        service_node = ServiceNode(id=service_node_id)
        service_node.related_services.add(service_id)
        self._save_object(obj)
        # TODO, why finish destroys the service?
        #servicesyncher.finish()
        return service_id

    def _save_object(self, obj):
        if obj._changed:
            obj.last_modified_time = datetime.now(UTC_TIMEZONE)
            obj.save()
    
    def _create_language_dict(self, value):
        lang_dict = {}
        for lang in LANGUAGES:
            lang_dict[lang] = value
        return lang_dict

    # todo generic with name param.
    def get_serivice_node_id(self):
        service_node = None
        service_node_id = None
        try:
            service_node = ServiceNode.objects.get(name=self.SERVICE_NODE_NAMES["fi"])
        except ServiceNode.DoesNotExist:    
            print("Service Node does not exist")   
            # Highest available id
            service_node_id = ServiceNode.objects.all().order_by("-id")[0].id+1
        else:
            print("Service nodeexists")
            service_node_id = service_node.id
        return service_node_id            

def import_gas_filling_stations(**kwargs):

    importer = GasFillingStationImporter(**kwargs)  
    service_node_id = importer.get_serivice_node_id() 
    service_id = importer.generate_gas_filling_station_service(service_node_id)
    importer.generate_gas_filling_station_service_node(service_node_id)
    importer.import_gas_filling_stations(service_id)
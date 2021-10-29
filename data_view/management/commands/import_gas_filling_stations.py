import os
import json
import logging
from django.core.management import BaseCommand

from data_view.importers.gas_filling_station import(
    get_filtered_gas_filling_station_objects,
    save_to_database,
    GAS_FILLING_STATIONS_URL
)
from data_view.models import ContentTypes
logger = logging.getLogger("django")

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(            
            "--test-mode",             
            nargs="+",
            default=False,
            help="Run script in test mode. Uses Generated pandas dataframe.",
        )       
    
    def handle(self, *args, **options):
        logger.info("Importing gas filling stations.")
        if options["test_mode"]:
            logger.info("Running gas filling station_importer in test mode.")
            f = open(os.getcwd()+"/"+ContentTypes._meta.app_label+"/tests/"+options["test_mode"], "r")
            json_data = json.load(f)
            objects = get_filtered_gas_filling_station_objects(json_data=json_data)       
        else:
            logger.info("Fetcing gas filling stations from: {}"\
                .format(GAS_FILLING_STATIONS_URL))            
            objects = get_filtered_gas_filling_station_objects()       
        save_to_database(objects)
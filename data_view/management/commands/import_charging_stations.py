import os
import logging
import json
from django.core.management import BaseCommand
from data_view.models import ContentTypes
from data_view.importers.charging_stations import(
    get_filtered_charging_station_objects,
    save_to_database,
    CHARGING_STATIONS_URL
)
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
        logger.info("Importing charging stations.")
        if options["test_mode"]:
            logger.info("Running charging_station_importer in test mode.")
            f = open(os.getcwd()+"/"+ContentTypes._meta.app_label+"/tests/"+options["test_mode"], "r")
            json_data = json.load(f)
        else:
            logger.info("Fetcing charging stations from: {}"\
                .format(CHARGING_STATIONS_URL))
            objects = get_filtered_charging_station_objects()
            save_to_database(objects)
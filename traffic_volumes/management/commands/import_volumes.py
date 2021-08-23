import logging
import requests
import csv
from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import Point

from traffic_volumes.models import Location, Observation

LOCATIONS_URL = "https://dev.turku.fi/datasets/ecocounter/liikennelaskimet.geojson"
OBSERATIONS_URL = "https://dev.turku.fi/datasets/ecocounter/2020/counters-15min.csv"
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Imports Turku Traffic Volumes"

    def save_locations(self):
        response_json = requests.get(LOCATIONS_URL).json()
        features = response_json["features"]
        saved = 0
        for feature in features:
            location = Location()
            name = feature["properties"]["Nimi"]
            if not Location.objects.filter(name=name).exists():                
                location.name = name
                lon = feature["geometry"]["coordinates"][0]
                lat = feature["geometry"]["coordinates"][1]
                point = Point(lon, lat)
                location.geom = point
                location.save()
                saved += 1

        logger.info("Retrived {numloc} locations, saved {saved} locations.".format(numloc=len(features), saved=saved))

    def handle(self, *args, **options):
        logger.info("Retrieving stations...")
        #self.save_locations()
        logger.info("Retrieving observations...")
        #csv_file = OBSERATIONS_URL

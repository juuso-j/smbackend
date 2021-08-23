import logging
import requests
import urllib
import csv
import math
import pandas as pd 
import io
from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import Point

from eco_counter.models import Location, Observation

LOCATIONS_URL = "https://dev.turku.fi/datasets/ecocounter/liikennelaskimet.geojson"
OBSERATIONS_URL = "https://dev.turku.fi/datasets/ecocounter/2020/counters-15min.csv"
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Imports Turku Traffic Volumes"
    columns = ['aika', 'Teatterisilta PK', 'Teatterisilta JP', 'Auransilta JP',
       'Auransilta JK', 'Piispanristi P PK', 'Teatterisilta PP',
       'Auransilta AK', 'Kirjastosilta PK', 'Piispanristi E PK',
       'Auransilta PP', 'Kirjastosilta JP', 'Raisiontie PP',
       'Teatteri ranta PK', 'Kirjastosilta JK', 'Teatteri ranta PP',
       'Teatteri ranta JP', 'Auransilta PK', 'Teatterisilta JK',
       'Piispanristi E PP', 'Raisiontie PK', 'Kirjastosilta PP',
       'Auransilta AP', 'Teatteri ranta JK', 'Piispanristi P PP']

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

    def save_observations(self):
        response =  urllib.request.urlopen(OBSERATIONS_URL) 
        lines = [l.decode('utf-8') for l in response.readlines()]     
        
        locations = {}
        #Table used to lookup location relation
        for location in Location.objects.all():
            locations[location.name] = location
       
        string_data = requests.get(OBSERATIONS_URL).content
        # TODO check the latest time and only newest
        data = pd.read_csv(io.StringIO(string_data.decode('utf-8')))[57600:]
        for index, row in data.iterrows():
            time = row["aika"] # 2021-08-23 00:00:00
            #Iterate trough columns and store a observation for every
            #Note the first col is the "aika" and is discarded, the rest are observation values
            for c in range(1,len(self.columns)):
                tmp = self.columns[c].split()
                type = ""
                name = ""
                for t in tmp:
                    #the type is always uppercase and has length of two
                    if t.isupper() and len(t)==2:                        
                        type += t
                    else:
                        if len(name)>0:
                            name += " "+t
                        else:
                            name += t
              
                observation = Observation()
                observation.location = locations[name]
                value = row[c]
                if math.isnan(value):
                    observation.value = None
                else:
                    observation.value = row[c]
                observation.time = time
                observation.type = type
                observation.save()
    def handle(self, *args, **options):
        logger.info("Retrieving stations...")
        self.save_locations()
        logger.info("Retrieving observations...")
        self.save_observations()
      

             
       

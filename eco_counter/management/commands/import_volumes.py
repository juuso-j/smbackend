import logging
import requests
import pytz
import csv
import math
import io
import pandas as pd 
import dateutil.parser
from datetime import datetime
from django.utils.timezone import make_aware
from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import Point

from eco_counter.models import Location, Day,Week, ImportState

LOCATIONS_URL = "https://dev.turku.fi/datasets/ecocounter/liikennelaskimet.geojson"
OBSERATIONS_URL = "https://dev.turku.fi/datasets/ecocounter/2020/counters-15min.csv"
#UTC_TIMEZONE = pytz.timezone("UTC")
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Imports Turku Traffic Volumes"
    # columns = ['aika', 'Teatterisilta PK', 'Teatterisilta JP', 'Auransilta JP',
    #    'Auransilta JK', 'Piispanristi P PK', 'Teatterisilta PP',
    #    'Auransilta AK', 'Kirjastosilta PK', 'Piispanristi E PK',
    #    'Auransilta PP', 'Kirjastosilta JP', 'Raisiontie PP',
    #    'Teatteri ranta PK', 'Kirjastosilta JK', 'Teatteri ranta PP',
    #    'Teatteri ranta JP', 'Auransilta PK', 'Teatterisilta JK',
    #    'Piispanristi E PP', 'Raisiontie PK', 'Kirjastosilta PP',
    #    'Auransilta AP', 'Teatteri ranta JK', 'Piispanristi P PP']

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
        
        locations = {}
        #Dict used to lookup location relations
        for location in Location.objects.all():
            locations[location.name] = location
       
        string_data = requests.get(OBSERATIONS_URL).content
        # TODO check the latest time and only newest
        import_state = ImportState.load()
        rows_imported = import_state.rows_imported
        # NOTE, hack to override state
        rows_imported = 0
        data = pd.read_csv(io.StringIO(string_data.decode('utf-8')))[rows_imported:]
        length = len(data)
        import_state.rows_imported = rows_imported + length
        
        #breakpoint()
        #NOTE, try to get rid o pndas dependency
        req = requests.get(OBSERATIONS_URL)
        buff = io.StringIO(req.text)
        #len(list(csvreader))
        csvreader = csv.DictReader(buff)
        
        #breakpoint()       
        #for index, row in data.iterrows():
        values = {}
        #Temporary store day for every location
        days = {}
        #TODO, current Week and Month
        for index, row in enumerate(csvreader):
            print(" . " + str(index), end = "")
            try:
                time = dateutil.parser.parse(row["aika"]) # 2021-08-23 00:00:00
                time = make_aware(time)
            except (pytz.exceptions.NonExistentTimeError, pytz.exceptions.AmbiguousTimeError):
                continue
            
            
            #Iterate trough columns and store a observation for every
            #Note the first col is the "aika" and is discarded, the rest are observation values
            
            #Build dict with locations as keys and values dicts with type as key                 
               
            #for c in range(1,len(self.columns)):
            # Build the values dict by iterating all cols in row.
            # Values dict store the row data in structured form. 
            # values dict is of type:
            # values[location][type] = value, e.g. values["TeatteriSilta"]["PK"] = 6
            for col in row:
                if col == "aika":
                    continue
                tmp = col.split()
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
               
                value = row[col]
                if value == "":
                     # TODO, what to do with None values
                    value = 0
                else:
                    value = int(value)
                # if math.isnan(value):
                #     value = 0
                
                if name not in values:
                    values[name]={}
                # if type exist in values, we add the new value to get the hourly sample
                if type in values[name]:                                     
                    values[name][type] = int(values[name][type]) + value
                else:
                    values[name][type] = value
               
            # Create day every 24*4 iteration
            if index % (24*4) == 0:
                print("DAYS mod 24*4")            
                
                days = {}
                for loc in locations:
                    day = Day.objects.create(date=time.date(), location=locations[loc])                  
                    #breakpoint()
                    print("created: ", day, end="")
                    days[loc] = day
                #breakpoint()
            
            #Add hour data every 4 iteration, sample rate is 15min
            if index % 4 == 0:
                for loc in values:                   
                    day = days[loc]
                    #breakpoint()
                    if "AK" and "AP" in values[loc]:
                        ak = values[loc]["AK"]
                        ap = values[loc]["AP"]
                        tot = ak+ap
                        #breakpoint()              
                        day.values_ak.append(ak)
                        day.values_ap.append(ap)
                        day.values_at.append(tot)
                    
                    if "PK" and "PP" in values[loc]:
                        pk = values[loc]["PK"]
                        pp = values[loc]["PP"]
                        tot = pk+pp              
                        day.values_pk.append(pk)
                        day.values_pp.append(pp)
                        day.values_pt.append(tot)
                    # store "jalankulkija" pedestrian info
                    if "JK" and "JP" in values[loc]:
                        jk = values[loc]["JK"]
                        jp = values[loc]["JP"]
                        tot = jk+jp              
                        day.values_jk.append(jk)
                        day.values_jp.append(jp)
                        day.values_jt.append(tot)  
                    day.save()
                #breakpoint()     
                # Clear values after storage
                values = {}
              
        
        import_state.save()


    def handle(self, *args, **options):
        logger.info("Retrieving stations...")
        self.save_locations()
        logger.info("Retrieving observations...")
        self.save_observations()
      

             
       

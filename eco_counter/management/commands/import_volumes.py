import logging
import requests
import pytz
import math
import io
import pandas as pd 
import dateutil.parser
from datetime import datetime
from django.utils.timezone import make_aware
from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import Point

from eco_counter.models import (
    Location, 
    Day,Week, 
    WeekDay,  
    WeekData,
    Month, 
    MonthData,
    Year, 
    YearData,
    ImportState

    )

LOCATIONS_URL = "https://dev.turku.fi/datasets/ecocounter/liikennelaskimet.geojson"
OBSERATIONS_URL = "https://dev.turku.fi/datasets/ecocounter/2020/counters-15min.csv"
GK25_SRID = 3879

#UTC_TIMEZONE = pytz.timezone("UTC")
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Imports Turku Traffic Volumes"
    
    # List used to lookup name and type
    # Output of pandas dataframe, i.e. data.keys()
    columns = ['aika', 'Teatterisilta PK', 'Teatterisilta JP', 'Auransilta JP',
       'Auransilta JK', 'Piispanristi P PK', 'Teatterisilta PP',
       'Auransilta AK', 'Kirjastosilta PK', 'Piispanristi E PK',
       'Auransilta PP', 'Kirjastosilta JP', 'Raisiontie PP',
       'Teatteri ranta PK', 'Kirjastosilta JK', 'Teatteri ranta PP',
       'Teatteri ranta JP', 'Auransilta PK', 'Teatterisilta JK',
       'Piispanristi E PP', 'Raisiontie PK', 'Kirjastosilta PP',
       'Auransilta AP', 'Teatteri ranta JK', 'Piispanristi P PP']
    
    def delete_tables(self):
        Day.objects.all().delete()
        WeekDay.objects.all().delete()
        WeekData.objects.all().delete()
        Week.objects.all().delete()
        Month.objects.all().delete()
        MonthData.objects.all().delete()

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
                point = Point(lat, lon)
                location.geom = point
                location.save()
                saved += 1

        logger.info("Retrived {numloc} locations, saved {saved} locations.".format(numloc=len(features), saved=saved))

    def get_dataframe(self, start_pos):
        string_data = requests.get(OBSERATIONS_URL).content
        data = pd.read_csv(io.StringIO(string_data.decode('utf-8')))[start_pos:]
        return data
        
    def save_observations(self):         
        self.delete_tables()
        locations = {}
        #Dict used to lookup location relations
        for location in Location.objects.all():
            locations[location.name] = location       

        # Holds 
        current_values = {}
        #Temporarly store references to day instances for every location(key) currenlty populating
        current_days = {}
        #Temporarly store references to week instances for every location(key) currently populating
        current_weeks = {}
        current_months = {}
      
        week_number = None
        prev_week_number = None
        month_number = None
        prev_month_number = None
        year = None

        # TODO check the latest time and only newest
        import_state = ImportState.load()
        rows_imported = import_state.rows_imported
        # TODO TODO fetch CURRENT YEARs current_months and week instances from state
        # NOTE, hack to override state
        rows_imported = 0
        data = self.get_dataframe(rows_imported)
        self.columns = data.keys()
        length = len(data)
        import_state.rows_imported = rows_imported + length              
         
        for index, row in data.iterrows():
            print(" . " + str(index), end = "")
            try:
                time = dateutil.parser.parse(row["aika"]) # 2021-08-23 00:00:00
                time = make_aware(time)
            except (pytz.exceptions.NonExistentTimeError, pytz.exceptions.AmbiguousTimeError):
                continue                    
            
            year, week_number, day_number = datetime.date(time).isocalendar()
            month_number = datetime.date(time).month

            if prev_month_number != month_number or not current_weeks:
                if prev_month_number != month_number and prev_month_number:
                    for location in locations:
                        month = current_months[location]
                        month_data = MonthData.objects.create(month=month, location=locations[location])
                        #breakpoint()
                        for mo in month.week_data.all():
                            month_data.value_ak += mo.value_ak
                            month_data.value_ap += mo.value_ap
                            month_data.value_at += mo.value_at
                            month_data.value_pk += mo.value_pk
                            month_data.value_pp += mo.value_pp
                            month_data.value_pt += mo.value_pt
                            month_data.value_jk += mo.value_jk
                            month_data.value_jp += mo.value_jp
                            month_data.value_jt += mo.value_jt                           
                        month_data.save()
                #         breakpoint()
                #         pass
                for location in locations:
                    month = Month.objects.create(location=locations[location], year=year, month_number=month_number)
                    current_months[location] = month
                
                prev_month_number = month_number


            if prev_week_number != week_number or not current_weeks:                
                #if week changed store weekly data
                if prev_week_number != week_number and prev_week_number:
                    for location in locations:
                        week = current_weeks[location]
                        week_data = WeekData.objects.create(week=week, location=locations[location], month=current_months[location])
                        for we in week.week_days.all():
                            week_data.value_ak += we.value_ak
                            week_data.value_ap += we.value_ap
                            week_data.value_at += we.value_at
                            week_data.value_pk += we.value_pk
                            week_data.value_pp += we.value_pp
                            week_data.value_pt += we.value_pt
                            week_data.value_jk += we.value_jk
                            week_data.value_jp += we.value_jp
                            week_data.value_jt += we.value_jt                           
                        week_data.save()
                for location in locations:
                    week = Week.objects.create(location=locations[location], year=year, week_number=week_number)
                    current_weeks[location] = week
                
                prev_week_number = week_number
                #breakpoint()

            # Build the current_values dict by iterating all cols in row.
            # current_Values dict store the row data in a structured form. 
            # current_values dict is of type:
            # current_values[location][type] = value, e.g. current_values["TeatteriSilta"]["PK"] = 6
            #for col in row:
            #Note the first col is the "aika" and is discarded, the rest are observated current_values
            for col in range(1, len(self.columns)):                
                tmp = self.columns[col].split()
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
                if math.isnan(value):
                    value = 0
               
                # # if math.isnan(value):
                #     value = 0
                
                if name not in current_values:
                    current_values[name]={}
                # if type exist in current_values, we add the new value to get the hourly sample
                if type in current_values[name]:                                     
                    current_values[name][type] = int(current_values[name][type]) + value
                else:
                    current_values[name][type] = value
               
            # Create day every 24*4  (24h*15min) iteration
            if index % (24*4) == 0:
                print("DAYS mod 24*4")           
               
                # Store the WeekDay object that contains the daily data(24 hour data samples)
                if current_days:
                    for location in locations:
                        tmp_day = current_days[location]
                        week_day = WeekDay.objects.create(location=locations[location],date=tmp_day.date, week=tmp_day.week)
                        week_day.value_ak = sum(tmp_day.values_ak)
                        week_day.value_ap = sum(tmp_day.values_ap)
                        week_day.value_at = sum(tmp_day.values_at)
                        week_day.value_pk = sum(tmp_day.values_pk)
                        week_day.value_pp = sum(tmp_day.values_pp)
                        week_day.value_pt = sum(tmp_day.values_pt)
                        week_day.value_jk = sum(tmp_day.values_jk)
                        week_day.value_jp = sum(tmp_day.values_jp)
                        week_day.value_jt = sum(tmp_day.values_jt)
                        week_day.save()
                        #breakpoint()
                current_days = {}
                for location in locations:
                    day = Day.objects.create(date=time.date(), location=locations[location], week=current_weeks[location], month=current_months[location])                   
                    current_days[location] = day
                #breakpoint()
            
            #Adds hour data every fourth iteration, sample rate is 15min
            if index % 4 == 0:
                for loc in current_values:                   
                    day = current_days[loc]
                    #breakpoint()
                    if "AK" and "AP" in current_values[loc]:
                        ak = current_values[loc]["AK"]
                        ap = current_values[loc]["AP"]
                        tot = ak+ap
                        day.values_ak.append(ak)
                        day.values_ap.append(ap)
                        day.values_at.append(tot)
                    
                    if "PK" and "PP" in current_values[loc]:
                        pk = current_values[loc]["PK"]
                        pp = current_values[loc]["PP"]
                        tot = pk+pp              
                        day.values_pk.append(pk)
                        day.values_pp.append(pp)
                        day.values_pt.append(tot)
                    # store "jalankulkija" pedestrian 
                    if "JK" and "JP" in current_values[loc]:
                        jk = current_values[loc]["JK"]
                        jp = current_values[loc]["JP"]
                        tot = jk+jp              
                        day.values_jk.append(jk)
                        day.values_jp.append(jp)
                        day.values_jt.append(tot)  
                    day.save()
                #breakpoint()     
                # Clear current_values after storage
                current_values = {}
              
        
        import_state.save()


    def handle(self, *args, **options):
        logger.info("Retrieving stations...")
        self.save_locations()
        logger.info("Retrieving observations...")
        self.save_observations()
      

             
       

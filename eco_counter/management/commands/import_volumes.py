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
logger.setLevel(logging.INFO)


class Command(BaseCommand):
    help = "Imports Turku Traffic Volumes"
    
    # List used to lookup name and type
    # Output of pandas dataframe, i.e. csv_data.keys()
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
        Year.objects.all().delete()
        YearData.objects.all().delete()
        #Location.objects.all().delete()
        ImportState.objects.all().delete()

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

    def get_dataframe(self):
        string_data = requests.get(OBSERATIONS_URL).content
        csv_data = pd.read_csv(io.StringIO(string_data.decode('utf-8')))
        return csv_data

    def calc_and_store_cum_data(self, src_obj, dst_obj):
        for src in src_obj:
            dst_obj.value_ak += src.value_ak
            dst_obj.value_ap += src.value_ap
            dst_obj.value_at += src.value_at
            dst_obj.value_pk += src.value_pk
            dst_obj.value_pp += src.value_pp
            dst_obj.value_pt += src.value_pt
            dst_obj.value_jk += src.value_jk
            dst_obj.value_jp += src.value_jp
            dst_obj.value_jt += src.value_jt 
        dst_obj.save()
         
    def save_and_calc_week_day(self, current_day, week_day):
        week_day.value_ak = sum(current_day.values_ak)
        week_day.value_ap = sum(current_day.values_ap)
        week_day.value_at = sum(current_day.values_at)
        week_day.value_pk = sum(current_day.values_pk)
        week_day.value_pp = sum(current_day.values_pp)
        week_day.value_pt = sum(current_day.values_pt)
        week_day.value_jk = sum(current_day.values_jk)
        week_day.value_jp = sum(current_day.values_jp)
        week_day.value_jt = sum(current_day.values_jt)
        week_day.save()
    
    def save_observations(self):         
        
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
        current_years = {}        
      

        import_state = ImportState.load()
        rows_imported = import_state.rows_imported
        current_year_number = import_state.current_year_number 
        current_month_number = import_state.current_month_number
        # week number is derived from the month
        current_week_number = None
        current_day_number = None    
        prev_year_number = current_year_number
        prev_month_number = current_month_number
        prev_week_number = None
        
        csv_data = self.get_dataframe()
        start_time = "{year}-{month}-1 00:00:00".format(year=import_state.current_year_number, month=import_state.current_month_number)
        start_time = dateutil.parser.parse(start_time)
        start_index = csv_data.index[csv_data["aika"]==str(start_time)].values[0]
        print("Start index:", start_index)
        csv_data = csv_data[start_index:]
       
        if True:
            for location in locations:
                print("location", location)
                current_years[location], created = Year.objects.get_or_create(location=locations[location], year_number=current_year_number)
                # if Year.objects.filter(location=locations[location], current_year_number=current_year_number).exists():
                #     print("Year exists")
                #     current_years[location] = Year.objects.get(location=locations[location], current_year_number=current_year_number)
                # else:
                #     current_years[location] = Year.objects.create(location=locations[location], current_year_number=current_year_number)
                current_months[location], created = Month.objects.get_or_create(location=locations[location], year=current_years[location], month_number=current_month_number)
                
                # if Month.objects.filter(location=locations[location], year=current_years[location], current_month_number=current_month_number).exists():
                #     print("Month exists")
                #     current_months[location] = Month.objects.get(location=locations[location], year=current_years[location], current_month_number=current_month_number)
                # else:
                #     current_months[location] = Month.objects.create(location=locations[location], year=current_years[location], current_month_number=current_month_number)
                
                Week.objects.filter(location=locations[location], year=current_years[location], month=current_months[location]).delete()
                
            current_week_number = start_time.isocalendar()[1]
            #prev_week_number = current_week_number
        self.columns = csv_data.keys()         
        
        for index, row in csv_data.iterrows():
            print(" . " + str(index), end = "")
            try:
                time = dateutil.parser.parse(row["aika"]) # 2021-08-23 00:00:00
                time = make_aware(time)
            except (pytz.exceptions.NonExistentTimeError, pytz.exceptions.AmbiguousTimeError):                               
                pass

            current_year_number, current_week_number, current_day_number = datetime.date(time).isocalendar()
            current_month_number = datetime.date(time).month
            # Add new year table if year does exist for every location and add references to state(current_years)
            if prev_year_number != current_year_number or not current_years:
                # if we have a prev_year_number and it is not the current_year_number store data.
                if prev_year_number:
                    for location in locations:
                        year = current_years[location]
                        year_data = YearData.objects.create(year=year, location=locations[location])
                        self.calc_and_store_cum_data(year.month_data.all(), year_data)
                    #self.calc_and_save_year_data(location, current_year)   
                for location in locations:
                    year = Year.objects.create(year_number=current_year_number, location=locations[location])
                    current_years[location] = year
                prev_year_number = current_year_number

            if prev_month_number != current_month_number or not current_months:
                if  prev_month_number:                    
                    for location in locations:
                        month = current_months[location]
                        month_data = MonthData.objects.create(month=month, location=locations[location], year=current_years[location])
                        self.calc_and_store_cum_data(month.week_data.all(), month_data)

                for location in locations:
                    month = Month.objects.create(location=locations[location], year=current_years[location], month_number=current_month_number)
                    current_months[location] = month
                
                prev_month_number = current_month_number


            if prev_week_number != current_week_number or not current_weeks:                
                #if week changed store weekly csv_data
                if prev_week_number:
                    for location in locations:
                        week = current_weeks[location]
                        week_data = WeekData.objects.create(week=week, location=locations[location], month=current_months[location])
                        self.calc_and_store_cum_data(week.week_days.all(), week_data)

                for location in locations:
                    week = Week.objects.create(location=locations[location], month=current_months[location], week_number=current_week_number, year=current_years[location])
                    current_weeks[location] = week
                
                prev_week_number = current_week_number
                #breakpoint()

            # Build the current_values dict by iterating all cols in row.
            # current_values dict store the rows csv_data in a structured form. 
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
                    if t.isupper() and len(t) == 2:                        
                        type += t
                    else:
                        if len(name) > 0:
                            name += " "+t
                        else:
                            name += t
               
                value = row[col]
                if math.isnan(value):
                    value = 0
               
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
              
                # Store the WeekDay object that contains the daily csv_data(24 hour csv_data samples)
                if current_days:
                    for location in locations:
                        current_day = current_days[location]
                        week_day = WeekDay.objects.create(location=locations[location], \
                            date=current_day.date, week=current_day.week, day_number=current_day_number)                       
                        self.save_and_calc_week_day(current_day, week_day)
                current_days = {}

                for location in locations:
                    day = Day.objects.create(date=time.date(), location=locations[location],\
                         week=current_weeks[location], month=current_months[location], day_number=current_day_number)                   
                    current_days[location] = day
            
            #Adds data for an hour every fourth iteration, sample rate is 15min
            if index % 4 == 0:
                for loc in current_values:                   
                    day = current_days[loc]
                    #TODO refactor to function
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
                # Clear current_values after storage, to get data for every hour
                current_values = {}
        # TODO calc the current year, mont and week data....
             
        import_state.current_year_number = current_year_number
        import_state.current_month_number = current_month_number
        import_state.rows_imported = rows_imported + len(csv_data)     
        import_state.save()

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete-tables",
            action="store_true",
            dest="delete-tables",
            default=False,
            help="Deletes tables before importing.",
        )

    def handle(self, *args, **options):
        logger.info("Retrieving stations...")
        
        if options["delete-tables"]:
            print("Deleting tables")
            self.delete_tables()

        self.save_locations()
        logger.info("Retrieving observations...")
        self.save_observations()
      

             
       

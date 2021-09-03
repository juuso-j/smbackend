"""
Brief explanation of the import alogithm:

1. Read the csv file as a pandas DataFrame
2. Reads the year and month from the ImportState 
3. Sets the import to begin from that year and month, the import always begins
 from the first day of the month in state, i.e. the longest timespan that is 
 imported is one month and the shortest 15min.
4. Set the current state to state variables: current_years, currents_months, 
 current_weeks, this dictionaries holds references to the model instances. 
 Every station has its own state variables, the key for the state variables
  is the station.
5. Iterate through all the rows
    5.1 Read the time
    5.2 Read the current year, month, week and day number
    5.3 If Year number has changed, save year data and create new year 
     instances with the new year and set to the current state
    5.4 If index % 4 == 0 save current hour, the input data has a sample rate
     of 15min, and the precision stored while importing is One hour.
    5.5 If day number has changed save day data.
    5.5.1 If month number has changed save the current month data and 
           create new instances and store the references to the state.
    5.5.2 Create new day instances and update state
    5.6 Iterate through all the columns, except the first that holds the time.
    5.6.1 Stores the sampled data to current_hours state for every station, 
         every mode of transportaion and direction.
    5.7 If week has changed store week data, create new instances and update
         state.
6. Finally store all data in state that has not been saved.
7. Save state.

"""

import logging
import requests
import pytz
import math
import io
import re
import pandas as pd 
import dateutil.parser
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import Point

from eco_counter.models import (
    Station, 
    Day,
    Week, 
    WeekDay,  
    WeekData,
    Month, 
    MonthData,
    Year, 
    YearData,
    ImportState
    )

STATIONS_URL = "https://dev.turku.fi/datasets/ecocounter/liikennelaskimet.geojson"
OBSERATIONS_URL = "https://dev.turku.fi/datasets/ecocounter/2020/counters-15min.csv"
GK25_SRID = 3879
# TODO create logger for this module!!!
logger = logging.getLogger("django")


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
        Station.objects.all().delete()
        ImportState.objects.all().delete()

    def get_dataframe(self):
        response = requests.get(OBSERATIONS_URL) 
        assert response.status_code == 200, "Fetching observations csv {} status code {}".\
            format(OBSERATIONS_URL, response.status_code)
        string_data = response.content
        csv_data = pd.read_csv(io.StringIO(string_data.decode('utf-8')))
        return csv_data

    def calc_and_save_cumulative_data(self, src_obj, dst_obj):
        dst_obj.value_ak = 0
        dst_obj.value_ap = 0
        dst_obj.value_at = 0
        dst_obj.value_pk = 0
        dst_obj.value_pp = 0
        dst_obj.value_pt = 0
        dst_obj.value_jk = 0
        dst_obj.value_jp = 0
        dst_obj.value_jt = 0 
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

    def create_and_save_year_data(self, stations, current_years):
        for station in stations:
            year = current_years[station]
            year_data = YearData.objects.update_or_create(year=year, station=stations[station])[0]
            self.calc_and_save_cumulative_data(year.month_data.all(), year_data)

    def create_and_save_month_data(self, stations, current_months, current_years):                 
        for station in stations:
            month = current_months[station]
            month_data = MonthData.objects.update_or_create(month=month,\
                 station=stations[station], year=current_years[station])[0]
            qs = WeekDay.objects.filter(month=month, month__year=current_years[station])
            self.calc_and_save_cumulative_data(qs, month_data)

    def create_and_save_week_data(self, stations, current_weeks):
        for station in stations:
            week = current_weeks[station]
            week_data = WeekData.objects.update_or_create(week=week, station=stations[station])[0]
            self.calc_and_save_cumulative_data(week.week_days.all(), week_data)

    def create_and_save_week_day(self, stations, current_days,current_day_number):
        for station in stations:
            current_day = current_days[station]
            week_day = WeekDay.objects.update_or_create(station=stations[station], \
                date=current_day.date, week=current_day.week, month=current_day.month, \
                    day_number=current_day_number)[0]                             
            self.save_and_calc_week_day(current_day, week_day)    

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

    def save_hours(self, current_hours, current_days):
        for station in current_hours:                   
            day = current_days[station]            
            # Store "Auto"
            if "AK" and "AP" in current_hours[station]:
                ak = current_hours[station]["AK"]
                ap = current_hours[station]["AP"]
                tot = ak+ap
                day.values_ak.append(ak)
                day.values_ap.append(ap)
                day.values_at.append(tot)
            # Store "Pyöräilijä"
            if "PK" and "PP" in current_hours[station]:
                pk = current_hours[station]["PK"]
                pp = current_hours[station]["PP"]
                tot = pk+pp              
                day.values_pk.append(pk)
                day.values_pp.append(pp)
                day.values_pt.append(tot)
            # store "Jalankulkija" pedestrian 
            if "JK" and "JP" in current_hours[station]:
                jk = current_hours[station]["JK"]
                jp = current_hours[station]["JP"]
                tot = jk+jp              
                day.values_jk.append(jk)
                day.values_jp.append(jp)
                day.values_jt.append(tot)  
            day.save()

    def save_locations(self):
        response = requests.get(STATIONS_URL)
        assert response.status_code == 200, "Fetching stations from {} , status code {}"\
            .format(STATIONS_URL, response.status_code)

        response_json = response.json()
        features = response_json["features"]
        saved = 0
        for feature in features:
            station = Station()
            name = feature["properties"]["Nimi"]            
            if not Station.objects.filter(name=name).exists():                
                station.name = name
                lon = feature["geometry"]["coordinates"][0]
                lat = feature["geometry"]["coordinates"][1]
                point = Point(lat, lon)
                station.geom = point
                station.save()
                saved += 1

        logger.info("Retrived {numloc} stations, saved {saved} stations.".\
            format(numloc=len(features), saved=saved))

    def gen_test_csv(self, keys, start_time, end_time):
        """
        Generates testdata for a given timespan, 
        for every 15min the value 1 is set.
        """
        df = pd.DataFrame(columns=keys)
        df.keys = keys
        cur_time = start_time
        c = 0
        while cur_time <= end_time:
            vals = [1 for x in range(24)]
            vals.insert(0, str(cur_time))
            df.loc[c] = vals
            cur_time = cur_time + timedelta(minutes=15)
            c += 1            
        return df       

    def save_observations(self, csv_data, start_time):         
        
        stations = {}
        #Dict used to lookup station relations
        for station in Station.objects.all():
            stations[station.name] = station     
      
        current_hours = {}
        current_days = {}
        current_weeks = {}
        current_months = {}
        current_years = {}      
      
        import_state = ImportState.load()
        rows_imported = import_state.rows_imported
        current_year_number = import_state.current_year_number 
        current_month_number = import_state.current_month_number
        current_week_number = import_state.current_week_number
        current_day_number = None

        prev_day_number = datetime.date(start_time).isocalendar()[2]         
        prev_year_number = current_year_number
        prev_month_number = current_month_number
        prev_week_number = current_week_number        

        #All Hourly and daily data from the current_month are delete thus they are repopulated         
        Day.objects.filter(month__year__year_number=current_year_number, \
            month__month_number=current_month_number).delete()
        WeekDay.objects.filter(month__month_number=current_month_number, \
            month__year__year_number=current_year_number).delete()
        # Set the current state before starting populating
        for station in stations:
            current_years[station] = Year.objects.get_or_create(station=stations[station], \
                year_number=current_year_number)[0]           
            current_months[station] = Month.objects.get_or_create(station=stations[station], \
                year=current_years[station], month_number=current_month_number)[0]            
            current_weeks[station] = Week.objects.get_or_create(station=stations[station],\
                 year=current_years[station], week_number=current_week_number)[0]
  
        for index, row in csv_data.iterrows():           
            print(" . " + str(index), end = "")
            try:
                current_time = dateutil.parser.parse(row["aika"]) # 2021-08-23 00:00:00
                current_time = make_aware(current_time)
            except pytz.exceptions.NonExistentTimeError as err:                           
                logging.warning("NonExistentTimeError at time: " + str(current_time) + " Err: " + str(err))
            except pytz.exceptions.AmbiguousTimeError as err:
                #For some reason raises sometimes AmibiousTimeError for times that seems to be ok. e.g. 2020-03-29 03:45:00
                logging.warning("AmibiguousTimeError at time: " + str(current_time) + " Err: " + str(err))

            current_year_number, current_week_number, current_day_number = datetime.date(current_time).isocalendar()
            current_month_number = datetime.date(current_time).month
            # Add new year table if year does exist for every station and add references to state(current_years)
            if prev_year_number != current_year_number or not current_years:
                # if we have a prev_year_number and it is not the current_year_number store yearly data.
                if prev_year_number:                   
                    self.create_and_save_year_data(stations, current_years)                       
                for station in stations:
                    year = Year.objects.create(year_number=current_year_number, station=stations[station])
                    current_years[station] = year
                prev_year_number = current_year_number               
                  
            #Adds data for an hour every fourth iteration, sample rate is 15min
            # Add 1 to avoid modulo by 0
            if (index) % 4 == 0:
                self.save_hours(current_hours, current_days)                
                # Clear current_hours after storage, to get data for every hour
                current_hours = {}
            
            # Create day table every 24*4  (24h*15min) iteration
            if prev_day_number != current_day_number or not current_days:  
                # Store the WeekDay object that contains the daily csv_data(24 hour csv_data samples)
                if current_days:
                    self.create_and_save_week_day(stations, current_days, prev_day_number)                                  
                current_days = {}

                # Save new month before creating days for correct relations
                if prev_month_number != current_month_number or not current_months:
                    if  prev_month_number:  
                        self.create_and_save_month_data(stations, current_months, current_years)                 
                    for station in stations:
                        month = Month.objects.create(station=stations[station],\
                            year=current_years[station], month_number=current_month_number)
                        current_months[station] = month                
                    prev_month_number = current_month_number             
                
                for station in stations:                    
                    day = Day.objects.create(date=current_time.date(), station=stations[station],\
                         week=current_weeks[station], month=current_months[station], day_number=current_day_number)                   
                    current_days[station] = day 
                prev_day_number = current_day_number             
           
                     
            # Build the current_hours dict by iterating all cols in row.
            # current_hours dict store the rows in a structured form. 
            # current_hours keys are stations and every field contains a dict with the type as its key
            # Types are A|P|J(types: Auto, Pyöräilijä, Jalankulkija) and direction P|K , e.g. "JK"
            # current_hours[station][station_type] = value, e.g. current_hours["TeatteriSilta"]["PK"] = 6
            #Note the first col is the "aika" and is discarded, the rest are observations for every station
            for column in self.columns[1:]: 
                #Station type is always: A|P|J + K|P           
                station_type = re.findall("[A-Z][A-Z]", column)[0]
                station_name = column.replace(station_type,"").strip()                
               
                value = row[column]
                if math.isnan(value):
                    value = 0               
                if station_name not in current_hours:
                    current_hours[station_name]={}
                # if type exist in current_hours, we add the new value to get the hourly sample
                if station_type in current_hours[station_name]:                                     
                    current_hours[station_name][station_type] = int(current_hours[station_name][station_type]) + value
                else:
                    current_hours[station_name][station_type] = value

            if prev_week_number != current_week_number or not current_weeks:                                  
                #if week changed store weekly data
                if prev_week_number:
                    self.create_and_save_week_data(stations, current_weeks)                 
                for station in stations:
                    week = Week.objects.create(station=stations[station],\
                        week_number=current_week_number, year=current_years[station])
                    current_weeks[station] = week                
                    day = current_days[station]
                    day.week = week
                prev_week_number = current_week_number  
       
        
        #Finally save hours, weekdays, months etc. that are not fully populated.
        self.save_hours(current_hours, current_days)  
        self.create_and_save_week_day(stations, current_days,current_day_number)                                
        self.create_and_save_week_data(stations, current_weeks)                 
        self.create_and_save_month_data(stations, current_months, current_years)                 
        self.create_and_save_year_data(stations, current_years)                     
        
        import_state.current_year_number = current_year_number
        import_state.current_month_number = current_month_number
        import_state.current_week_number = current_week_number
        import_state.rows_imported = rows_imported + len(csv_data)     
        import_state.save()
        logger.info("Imported observation to: "+str(current_time))

    def add_arguments(self, parser):
        parser.add_argument(           
            "--delete-tables",
            action="store_true",
            default=False,
            help="Deletes tables before importing. Importing starts from row 0.",
        )
        parser.add_argument(            
            "--test-mode", 
            type=int,
            nargs="+",
            default=False,
            help="Run script in test mode.",
        )

    def handle(self, *args, **options):
        if  options["delete_tables"]:
            logger.info("Deleting tables")
            self.delete_tables()

        logger.info("Retrieving stations...")
        self.save_locations()      
        logger.info("Retrieving observations...")
        csv_data = self.get_dataframe()
        start_time = None
        if options["test_mode"]:
            logger.info("Retrieving observations in test mode.")
            start_time = options["test_mode"][0]
            csv_data = self.gen_test_csv(csv_data.keys(), start_time, options["test_mode"][1]) 
            #start_time = dateutil.parser.parse("2020-01-01 00:00:00")            
        else:
            self.columns = csv_data.keys()         
            import_state = ImportState.load() 
            start_time = "{year}-{month}-1 00:00:00".format(year=import_state.current_year_number, \
                month=import_state.current_month_number)
            start_time = dateutil.parser.parse(start_time)
            start_index = csv_data.index[csv_data["aika"]==str(start_time)].values[0]
            logger.info("Starting import at index: {}".format(start_index))
            csv_data = csv_data[start_index:]
        self.save_observations(csv_data, start_time)
      

             
       

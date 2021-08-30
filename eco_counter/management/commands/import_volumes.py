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

LOCATIONS_URL = "https://dev.turku.fi/datasets/ecocounter/liikennelaskimet.geojson"
OBSERATIONS_URL = "https://dev.turku.fi/datasets/ecocounter/2020/counters-15min.csv"
GK25_SRID = 3879

#UTC_TIMEZONE = pytz.timezone("UTC")
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

    def save_locations(self):
        response_json = requests.get(LOCATIONS_URL).json()
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

        logger.info("Retrived {numloc} stations, saved {saved} stations.".format(numloc=len(features), saved=saved))

    def get_dataframe(self):
        string_data = requests.get(OBSERATIONS_URL).content
        csv_data = pd.read_csv(io.StringIO(string_data.decode('utf-8')))
        return csv_data

    def calc_and_save_cum_data(self, src_obj, dst_obj):
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
            self.calc_and_save_cum_data(year.month_data.all(), year_data)

    def create_and_save_month_data(self, stations, current_months, current_years):                 
        for station in stations:
            month = current_months[station]
            month_data = MonthData.objects.update_or_create(month=month,\
                 station=stations[station], year=current_years[station])[0]
            self.calc_and_save_cum_data(month.week_data.all(), month_data)

    def create_and_save_week_data(self, stations, current_weeks, current_months):
        for station in stations:
            week = current_weeks[station]
            week_data = WeekData.objects.update_or_create(week=week, station=stations[station], month=current_months[station])[0]
            self.calc_and_save_cum_data(week.week_days.all(), week_data)

    def create_and_save_week_day(self, stations, current_days,current_day_number):
        for station in stations:
            current_day = current_days[station]
            week_day = WeekDay.objects.update_or_create(station=stations[station], \
                date=current_day.date, week=current_day.week, day_number=current_day_number)[0]                       
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

    def save_day(self, current_hours, current_days):
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
    
    def save_observations(self):         
        
        stations = {}
        #Dict used to lookup station relations
        for station in Station.objects.all():
            stations[station.name] = station       

        # Holds 
        current_hours = {}
        #Temporarly store references to day instances for every station(key) currenlty populating
        current_days = {}
        #Temporarly store references to week instances for every station(key) currently populating
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
        # We start import from the first day and time 00:00:00 of the current_mont
        
        start_time = "{year}-{month}-1 00:00:00".format(year=import_state.current_year_number, month=import_state.current_month_number)
        start_time = dateutil.parser.parse(start_time)
        start_index = csv_data.index[csv_data["aika"]==str(start_time)].values[0]
        logger.info("Starting import from index: {}".format(start_index))
        csv_data = csv_data[start_index:]
       
        for station in stations:
            current_years[station] = Year.objects.get_or_create(station=stations[station], \
                year_number=current_year_number)[0]           
            current_months[station] = Month.objects.get_or_create(station=stations[station], \
                year=current_years[station], month_number=current_month_number)[0]
            #All weeks from the current_month are delete thus they are repopulated
            Week.objects.filter(station=stations[station], year=current_years[station],\
                 month=current_months[station]).delete()
            
        current_week_number = start_time.isocalendar()[1]         
        self.columns = csv_data.keys()         
        
        for index, row in csv_data.iterrows():
            print(" . " + str(index), end = "")
            try:
                time = dateutil.parser.parse(row["aika"]) # 2021-08-23 00:00:00
                time = make_aware(time)
            except pytz.exceptions.NonExistentTimeError:                           
                logging.warning("NonExistentTimeError at time: "+str(time))
            except pytz.exceptions.AmbiguousTimeError:
                logging.warning("AmibiguousTimeError at time: "+str(time))

            current_year_number, current_week_number, current_day_number = datetime.date(time).isocalendar()
            current_month_number = datetime.date(time).month
            # Add new year table if year does exist for every station and add references to state(current_years)
            if prev_year_number != current_year_number or not current_years:
                # if we have a prev_year_number and it is not the current_year_number store data.
                if prev_year_number:                   
                    self.create_and_save_year_data(stations, current_years)                       
                for station in stations:
                    year = Year.objects.create(year_number=current_year_number, station=stations[station])
                    current_years[station] = year
                prev_year_number = current_year_number

            if prev_month_number != current_month_number or not current_months:
                if  prev_month_number:  
                    self.create_and_save_month_data(stations, current_months, current_years)                 
                for station in stations:
                    month = Month.objects.create(station=stations[station], year=current_years[station], month_number=current_month_number)
                    current_months[station] = month                
                prev_month_number = current_month_number

            if prev_week_number != current_week_number or not current_weeks:                
                #if week changed store weekly data
                if prev_week_number:
                    self.create_and_save_week_data(stations, current_weeks, current_months)                 
                for station in stations:
                    week = Week.objects.create(station=stations[station], month=current_months[station], week_number=current_week_number, year=current_years[station])
                    current_weeks[station] = week                
                prev_week_number = current_week_number

            # Build the current_hours dict by iterating all cols in row.
            # current_hours dict store the rows csv_data in a structured form. 
            # current_hours dict is of type:
            # current_hours[station][type] = value, e.g. current_hours["TeatteriSilta"]["PK"] = 6
            #for col in row:
            #Note the first col is the "aika" and is discarded, the rest are observated current_hours
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
                if name not in current_hours:
                    current_hours[name]={}
                # if type exist in current_hours, we add the new value to get the hourly sample
                if type in current_hours[name]:                                     
                    current_hours[name][type] = int(current_hours[name][type]) + value
                else:
                    current_hours[name][type] = value
               
            # Create day table every 24*4  (24h*15min) iteration
            if index % (24*4) == 0:   
                # Store the WeekDay object that contains the daily csv_data(24 hour csv_data samples)
                if current_days:
                    self.create_and_save_week_day(stations, current_days,current_day_number)                                    
                current_days = {}
                for station in stations:
                    day = Day.objects.create(date=time.date(), station=stations[station],\
                         week=current_weeks[station], month=current_months[station], day_number=current_day_number)                   
                    current_days[station] = day
            
            #Adds data for an hour every fourth iteration, sample rate is 15min
            if index % 4 == 0:
                self.save_day(current_hours, current_days)                
                # Clear current_hours after storage, to get data for every hour
                current_hours = {}
        
        
        # TODO calc the current year, mont and week data....
        self.save_day(current_hours, current_days)  
        self.create_and_save_week_day(stations, current_days,current_day_number)                                
        
        self.create_and_save_week_data(stations, current_weeks, current_months)                 
        self.create_and_save_month_data(stations, current_months, current_years)                 
        self.create_and_save_year_data(stations, current_years)                       
        

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
      

             
       

from io import StringIO
import dateutil.parser
from datetime import time, timedelta
import calendar
from django.db import reset_queries
from django.test import TestCase
from django.core.management import call_command
from django.test.testcases import SimpleTestCase

from eco_counter.models import (
    Station,
    HourData,
    Week, 
    Day,
    DayData,  
    WeekData,
    Month, 
    MonthData,
    Year, 
    YearData,
    ImportState
    )


NUM_STATIONS = 7

class ImporterTest(TestCase):
    def import_command(self, *args, **kwargs):
        out = StringIO()
        call_command(
            "import_eco_counter",
            *args,
            stdout=out,
            stderr=StringIO(),
            **kwargs,
        )
        return out.getvalue()
    
    
    """
    In test data, for every 15min the value 1 is set, so the sum for an hour is 4.
    For a day the sum is 96(24*4) and for a week 682(96*7). 
    The month sum depends on how  many days the month has,~3000 
    1.1.2020 is used as the starting point thus it is the same 
    starting point as in the real data.
    """
    def test_import(self):
        start_time = dateutil.parser.parse("2020-01-01 00:00:00")
        end_time = dateutil.parser.parse("2020-02-29 23:45:45")
        
        out = self.import_command(test_mode=(start_time, end_time))
        self.assertEqual(Station.objects.all().count(), NUM_STATIONS)
        # Test hourly data    
        # Auransilta is the only station that observes bicycles, pedestrains and cars
        hour_data = HourData.objects.get(station__name="Auransilta", day__date=start_time)
        res = [4 for x in range(24)]
        res_tot = [8 for x in range(24)]
        self.assertListEqual(hour_data.values_ap,res)
        self.assertListEqual(hour_data.values_ak,res) 
        self.assertListEqual(hour_data.values_at,res_tot)       
        self.assertListEqual(hour_data.values_pp,res) 
        self.assertListEqual(hour_data.values_pk,res) 
        self.assertListEqual(hour_data.values_pt,res_tot) 
        self.assertListEqual(hour_data.values_jk,res) 
        self.assertListEqual(hour_data.values_jp,res) 
        self.assertListEqual(hour_data.values_jt,res_tot)         
        
        # Test day data
        day = Day.objects.filter(date=start_time, station__name="Auransilta")[0]
        self.assertEqual(day.day_number, 2) # First day in 2020 in is wednesday
        day_data = DayData.objects.filter(day__date=start_time, station__name="Auransilta")[0]
        self.assertEqual(day_data.value_jp, 96)
        day_data = DayData.objects.filter(day__week__week_number=2, station__name="Auransilta")[0]
        self.assertEqual(day_data.value_jt, 96*2)
        day = Day.objects.filter(date=dateutil.parser.parse("2020-01-06 00:00:00"), station__name="Auransilta")[0]
        self.assertEqual(day.day_number, 0) # First day in week 2 in 2020 is monday
        # Test week data      
        week_data =  WeekData.objects.filter(week__week_number=1)[0]
        week = Week.objects.filter(week_number=1)[0]        
        self.assertEqual(week.days.count(),5) # first week of 2020 has only 5 days.
        self.assertEqual(week_data.value_jp, 480) # 5*96
        week_data =  WeekData.objects.filter(week__week_number=2)[0]
        week = Week.objects.filter(week_number=2)[0]
        self.assertEqual(week.days.count(),7) # second week of 2020 7 days.
        self.assertEqual(week_data.value_jp, 672) # 96*7 
        self.assertEqual(week_data.value_jk, 672) # 96*7 
        self.assertEqual(week_data.value_jt, 672*2) # 96*7 
        self.assertEqual(week.days.all().count(), NUM_STATIONS)
        #Test month data
        month = Month.objects.filter(month_number=1, year__year_number=2020)[0]
        num_month_days = month.days.all().count()
        jan_month_days = calendar.monthrange(month.year.year_number, month.month_number)[1]
        self.assertEqual(num_month_days, jan_month_days)
        month_data = MonthData.objects.get(month=month)
        self.assertEqual(month_data.value_pp, jan_month_days*96)
        self.assertEqual(month_data.value_pk, jan_month_days*96)
        self.assertEqual(month_data.value_pt, jan_month_days*96*2)
        month = Month.objects.filter(month_number=2, year__year_number=2020)[0]
        num_month_days = month.days.all().count()
        feb_month_days = calendar.monthrange(month.year.year_number, month.month_number)[1]
        self.assertEqual(num_month_days, feb_month_days)
        month_data = MonthData.objects.get(month=month)
        self.assertEqual(month_data.value_jp, feb_month_days*96)
        self.assertEqual(month_data.value_jk, feb_month_days*96)
        self.assertEqual(month_data.value_jt, feb_month_days*96*2)
        # test that number of days match
        self.assertEqual(Day.objects.filter(station__name="Auransilta").count(), jan_month_days+feb_month_days)
        year_data = YearData.objects.get(pk=1)       
        self.assertEqual(year_data.value_jp, jan_month_days*96+feb_month_days*96)
        # test state
        state = ImportState.load()
        self.assertEqual(state.current_month_number,2)
        self.assertEqual(state.current_year_number, 2020)
        week = Week.objects.filter(week_number=5)[0]        
        self.assertEqual(week.days.all().count(), NUM_STATIONS)
        # test incremental importing
        start_time = dateutil.parser.parse("2020-02-01 00:00:00")
        end_time = dateutil.parser.parse("2020-03-31 23:45:45")                
        out = self.import_command(test_mode=(start_time, end_time))
        # test that state is updated
        state = ImportState.load()
        self.assertEqual(state.current_month_number,3)
        self.assertEqual(state.current_year_number, 2020)
        # test that number of days in weeks remains intact
        week = Week.objects.filter(week_number=5)[0]       
        self.assertEqual(week.days.all().count(), NUM_STATIONS)
        week = Week.objects.filter(week_number=6)[0]        
        self.assertEqual(week.days.all().count(), NUM_STATIONS)
        # Test that we do not get multiple weeks
        self.assertEqual(Week.objects.filter(week_number=6).count(), NUM_STATIONS)
        day_data = DayData.objects.filter(day__week__week_number=10, station__name="Auransilta")[0]
        self.assertEqual(day_data.value_jt, 96*2)
        
        # Test week in previous month
        week_data =  WeekData.objects.filter(week__week_number=8)[0]
        week = Week.objects.filter(week_number=8)[0]
        self.assertEqual(week.days.all().count(),7) # week number 8 in 2020  has 7 days.
        self.assertEqual(week_data.value_jp, 672) 
        # Test starting month
        self.assertEqual(num_month_days, feb_month_days)
        month_data = MonthData.objects.get(month=month)
        self.assertEqual(month_data.value_jp, feb_month_days*96)
        
        # Test new month
        month = Month.objects.filter(month_number=3, year__year_number=2020)[0]
        num_month_days = month.days.all().count()
        mar_month_days = calendar.monthrange(month.year.year_number, month.month_number)[1]
        self.assertEqual(num_month_days, mar_month_days)
        month_data = MonthData.objects.get(month=month)
        self.assertEqual(month_data.value_jp, mar_month_days*96)
        
        year_data = YearData.objects.filter(year__year_number=2020)[0]       
        self.assertEqual(year_data.value_jp, jan_month_days*96+feb_month_days*96+mar_month_days*96)
   
        # Test new year
        start_time = dateutil.parser.parse("2021-09-01 00:00:00")
        end_time = dateutil.parser.parse("2021-09-30 23:45:45")        
        out = self.import_command(test_mode=(start_time, end_time))
        
        week_data =  WeekData.objects.filter(week__week_number=35)[0]
        week = Week.objects.filter(week_number=1)[0]        
        self.assertEqual(week.days.count(),5) #  week 35 in 2021 has only 5 days.
        self.assertEqual(week_data.value_jp, 480) # 5*96
        week_data =  WeekData.objects.filter(week__week_number=2)[0]
        week = Week.objects.filter(week_number=36)[0]
        self.assertEqual(week.days.count(),7) # week 36 in 2021 has 7 days.
        self.assertEqual(week_data.value_jp, 672) # 96*7 
        month = Month.objects.filter(month_number=9, year__year_number=2021)[0]
        num_month_days = month.days.all().count()
        sep_month_days = calendar.monthrange(month.year.year_number, month.month_number)[1]
        self.assertEqual(num_month_days, sep_month_days)
        month_data = MonthData.objects.get(month=month)
        self.assertEqual(month_data.value_jp, sep_month_days*96)
        
        year_data = YearData.objects.filter(year__year_number=2021)[0]
        self.assertEqual(year_data.value_pp, sep_month_days*96)       
        # verify that previous year is intact
        year_data = YearData.objects.filter(year__year_number=2020)[0]       
        self.assertEqual(year_data.value_pp, jan_month_days*96+feb_month_days*96+mar_month_days*96)
        # test that state is updated
        state = ImportState.load()
        self.assertEqual(state.current_month_number,9)
        self.assertEqual(state.current_year_number, 2021)

       

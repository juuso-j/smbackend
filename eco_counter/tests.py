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
        # Test hourly data    
        # Auransilta is the only station that observes bicycles, pedestrains and cars
        day = Day.objects.get(station__name="Auransilta", date=start_time)
        res = [4 for x in range(24)]
        res_tot = [8 for x in range(24)]
        self.assertListEqual(day.values_ap,res)
        self.assertListEqual(day.values_ak,res) 
        self.assertListEqual(day.values_at,res_tot)       
        self.assertListEqual(day.values_pp,res) 
        self.assertListEqual(day.values_pk,res) 
        self.assertListEqual(day.values_pt,res_tot) 
        self.assertListEqual(day.values_jk,res) 
        self.assertListEqual(day.values_jp,res) 
        self.assertListEqual(day.values_jt,res_tot)         
        
        # Test day data
        week_day = WeekDay.objects.filter(date=start_time, station__name="Auransilta")[0]
        self.assertEqual(week_day.day_number, 3) # First day in 2020 in is wednesday
        self.assertEqual(week_day.value_jp, 96)
        week_day = WeekDay.objects.filter(week__week_number=2, station__name="Auransilta")[0]
        self.assertEqual(week_day.day_number, 1) # First day in week 2 in 2020 is wednesday
        self.assertEqual(week_day.value_jt, 96*2)
       
        # Test week data      
        week_data =  WeekData.objects.filter(week__week_number=1)[0]
        week = Week.objects.filter(week_number=1)[0]        
        self.assertEqual(week.week_days.count(),5) # first week of 2020 has only 5 days.
        self.assertEqual(week_data.value_jp, 480) # 5*96
        week_data =  WeekData.objects.filter(week__week_number=2)[0]
        week = Week.objects.filter(week_number=2)[0]
        self.assertEqual(week.week_days.count(),7) # second week of 2020 7 days.
        self.assertEqual(week_data.value_jp, 672) # 96*7 
        self.assertEqual(week_data.value_jk, 672) # 96*7 
        self.assertEqual(week_data.value_jt, 672*2) # 96*7 
        
        #Test month data
        month = Month.objects.filter(month_number=1, year__year_number=2020)[0]
        num_month_days = month.week_days.all().count()
        jan_month_days = calendar.monthrange(month.year.year_number, month.month_number)[1]
        self.assertEqual(num_month_days, jan_month_days)
        month_data = MonthData.objects.get(month=month)
        self.assertEqual(month_data.value_pp, jan_month_days*96)
        self.assertEqual(month_data.value_pk, jan_month_days*96)
        self.assertEqual(month_data.value_pt, jan_month_days*96*2)

        month = Month.objects.filter(month_number=2, year__year_number=2020)[0]
        num_month_days = month.week_days.all().count()
        feb_month_days = calendar.monthrange(month.year.year_number, month.month_number)[1]
        self.assertEqual(num_month_days, feb_month_days)
        month_data = MonthData.objects.get(month=month)
        self.assertEqual(month_data.value_jp, feb_month_days*96)
        self.assertEqual(month_data.value_jk, feb_month_days*96)
        self.assertEqual(month_data.value_jt, feb_month_days*96*2)

        year_data = YearData.objects.get(pk=1)       
        self.assertEqual(year_data.value_jp, jan_month_days*96+feb_month_days*96)
        
        # test incremental importing
        start_time = dateutil.parser.parse("2020-02-1 00:00:00")
        end_time = dateutil.parser.parse("2020-03-31 23:45:45")        
        out = self.import_command(test_mode=(start_time, end_time))
        week_day = WeekDay.objects.filter(week__week_number=10, station__name="Auransilta")[0]
        self.assertEqual(week_day.day_number, 1) # First day in week 2 in 2020 is wednesday
        self.assertEqual(week_day.value_jt, 96*2)
        # Test week in previous month
        week_data =  WeekData.objects.filter(week__week_number=8)[0]
        week = Week.objects.filter(week_number=2)[0]
        self.assertEqual(week.week_days.count(),7) # week number 8 in 2020  has 7 days.
        self.assertEqual(week_data.value_jp, 672) 
        # Test starting month
        self.assertEqual(num_month_days, feb_month_days)
        month_data = MonthData.objects.get(month=month)
        self.assertEqual(month_data.value_jp, feb_month_days*96)
        
        # Test new month
        month = Month.objects.filter(month_number=3, year__year_number=2020)[0]
        num_month_days = month.week_days.all().count()
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
        month = Month.objects.filter(month_number=9, year__year_number=2021)[0]
        num_month_days = month.week_days.all().count()
        sep_month_days = calendar.monthrange(month.year.year_number, month.month_number)[1]
        self.assertEqual(num_month_days, sep_month_days)
        month_data = MonthData.objects.get(month=month)
        self.assertEqual(month_data.value_jp, sep_month_days*96)
        
        year_data = YearData.objects.filter(year__year_number=2021)[0]
        self.assertEqual(year_data.value_pp, sep_month_days*96)       
        # verify that previous year is intact
        year_data = YearData.objects.filter(year__year_number=2020)[0]       
        self.assertEqual(year_data.value_pp, jan_month_days*96+feb_month_days*96+mar_month_days*96)
   

       

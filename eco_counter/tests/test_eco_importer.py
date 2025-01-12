from io import StringIO
import dateutil.parser
from datetime import time, timedelta
import calendar
import pytest
from django.core.management import call_command
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

TEST_STATION_NAME = "Auransilta"

def import_command(*args, **kwargs):
        out = StringIO()
        call_command(
            "import_eco_counter",
            *args,
            stdout=out,
            stderr=StringIO(),
            **kwargs,
        )
        return out.getvalue()

@pytest.mark.slow
@pytest.mark.django_db
def test_importer():
    """
    In test data, for every 15min the value 1 is set, so the sum for an hour is 4.
    For a day the sum is 96(24*4) and for a week 682(96*7). 
    The month sum depends on how  many days the month has,~3000 
    1.1.2020 is used as the starting point thus it is the same 
    starting point as in the real data.
    """
    start_time = dateutil.parser.parse("2020-01-01 00:00:00")
    end_time = dateutil.parser.parse("2020-02-29 23:45:45")        
    out = import_command(test_mode=(start_time, end_time))

    num_stations = Station.objects.all().count()
    assert Station.objects.get(name=TEST_STATION_NAME) 
    
    # Test hourly data    
    #TEST_STAION_NAMEis the only station that observes bicycles, pedestrains and cars
    hour_data = HourData.objects.get(station__name=TEST_STATION_NAME, day__date=start_time)
    res = [4 for x in range(24)]
    res_tot = [8 for x in range(24)]
    assert hour_data.values_ap == res
    assert hour_data.values_ak == res 
    assert hour_data.values_at == res_tot         
    assert hour_data.values_pp == res 
    assert hour_data.values_pk == res 
    assert hour_data.values_pt == res_tot   
    assert hour_data.values_jk == res 
    assert hour_data.values_jp == res 
    assert hour_data.values_jt == res_tot     
    # Test day data
    day = Day.objects.filter(date=start_time, station__name=TEST_STATION_NAME)[0]
    assert day.weekday_number == 2 # First day in 2020 in is wednesday
    day_data = DayData.objects.filter(day__date=start_time, station__name=TEST_STATION_NAME)[0]
    assert day_data.value_jp == 96
    day_data = DayData.objects.filter(day__week__week_number=2, station__name=TEST_STATION_NAME)[0]
    assert day_data.value_jt == 96*2
    day = Day.objects.filter(date=dateutil.parser.parse("2020-01-06 00:00:00"), station__name=TEST_STATION_NAME)[0]
    assert day.weekday_number == 0 # First day in week 2 in 2020 is monday

    # Test week data      
    week_data =  WeekData.objects.filter(week__week_number=1)[0]
    week = Week.objects.filter(week_number=1)[0]  
    # first week of 2020 has only 5 days, thus it is the start of the import      
    assert week.days.count() == 5
    assert week_data.value_jp == 480 # 5*96
    week_data =  WeekData.objects.filter(week__week_number=2)[0]
    week = Week.objects.filter(week_number=2)[0]
    assert week.days.count() == 7 # second week of 2020 7 days.
    assert week_data.value_jp == 672 # 96*7 
    assert week_data.value_jk == 672 # 96*7 
    assert week_data.value_jt == 672*2 # 96*7 
    assert Week.objects.filter(week_number=2).count() == num_stations
    assert WeekData.objects.filter(week__week_number=2).count() == num_stations
    # Test month data
    month = Month.objects.filter(month_number=1, year__year_number=2020)[0]
    num_month_days = month.days.all().count()
    jan_month_days = calendar.monthrange(month.year.year_number, month.month_number)[1]
    assert num_month_days == jan_month_days
    month_data = MonthData.objects.get(month=month)
    assert month_data.value_pp == jan_month_days*96
    assert month_data.value_pk == jan_month_days*96
    assert month_data.value_pt == jan_month_days*96*2
    month = Month.objects.filter(month_number=2, year__year_number=2020)[0]
    num_month_days = month.days.all().count()
    feb_month_days = calendar.monthrange(month.year.year_number, month.month_number)[1]
    assert num_month_days == feb_month_days
    month_data = MonthData.objects.get(month=month)
    assert month_data.value_jp == feb_month_days*96
    assert month_data.value_jk == feb_month_days*96
    assert month_data.value_jt== feb_month_days*96*2
    # test that number of days match
    assert Day.objects.filter(station__name=TEST_STATION_NAME).count() == jan_month_days+feb_month_days
    year_data = YearData.objects.get(station__name=TEST_STATION_NAME, year__year_number=2020)       
    assert year_data.value_jp == jan_month_days*96+feb_month_days*96
    assert Year.objects.get(station__name=TEST_STATION_NAME, year_number=2020) 
    # test state
    state = ImportState.load()
    assert state.current_month_number == 2
    assert state.current_year_number == 2020
    week = Week.objects.filter(week_number=5)[0]        
    assert week.days.all().count() == num_stations
    # test incremental importing
    start_time = dateutil.parser.parse("2020-02-01 00:00:00")
    end_time = dateutil.parser.parse("2020-03-31 23:45:45")                
    out = import_command(test_mode=(start_time, end_time))
    # test that state is updated
    state = ImportState.load()
    assert state.current_month_number ==3
    assert state.current_year_number == 2020
    # test that number of days in weeks remains intact
    week = Week.objects.filter(week_number=5)[0]       
    assert week.days.all().count() == 7
    week = Week.objects.filter(week_number=6)[0]        
    assert week.days.all().count() == 7
    # Test that we do not get multiple weeks
    assert Week.objects.filter(week_number=6).count() == num_stations
    assert WeekData.objects.filter(week__week_number=6).count() == num_stations
    day_data = DayData.objects.filter(day__week__week_number=10, station__name=TEST_STATION_NAME)[0]
    assert day_data.value_jt == 96*2
    # Test week in previous month
    week_data =  WeekData.objects.filter(week__week_number=8)[0]
    week = Week.objects.filter(week_number=8)[0]
    assert week.days.all().count() == 7 
    assert week_data.value_jp == 672 
    # Test starting month
    assert num_month_days == feb_month_days
    month_data = MonthData.objects.get(month=month)
    assert month_data.value_jp == feb_month_days*96
    # Test new month
    month = Month.objects.filter(month_number=3, year__year_number=2020)[0]
    num_month_days = month.days.all().count()
    mar_month_days = calendar.monthrange(month.year.year_number, month.month_number)[1]
    assert num_month_days == mar_month_days
    month_data = MonthData.objects.get(month=month)
    assert month_data.value_jp == mar_month_days*96        
    year_data = YearData.objects.filter(year__year_number=2020)[0]       
    assert year_data.value_jp == (jan_month_days*96+feb_month_days*96+mar_month_days*96)
    # Test new year
    start_time = dateutil.parser.parse("2021-09-01 00:00:00")
    end_time = dateutil.parser.parse("2021-09-30 23:45:45")        
    out = import_command(test_mode=(start_time, end_time))      
    assert Year.objects.get(station__name=TEST_STATION_NAME, year_number=2020) 
    assert Year.objects.get(station__name=TEST_STATION_NAME, year_number=2021)   
    week_data =  WeekData.objects.filter(week__week_number=35,week__years__year_number=2021)[0]
    week = Week.objects.filter(week_number=35, years__year_number=2020)[0]        
    assert week.days.count() == 5 #  week 35 in 2021 has only 5 days.
    assert week_data.value_jp == 480 # 5*96
    week_data =  WeekData.objects.filter(week__week_number=36)[0]
    week = Week.objects.filter(week_number=36)[0]
    assert week.days.count() == 7 # week 36 in 2021 has 7 days.
    assert week_data.value_jp == 672 # 96*7 
    month = Month.objects.filter(month_number=9, year__year_number=2021)[0]
    num_month_days = month.days.all().count()
    sep_month_days = calendar.monthrange(month.year.year_number, month.month_number)[1]
    assert num_month_days == sep_month_days
    month_data = MonthData.objects.get(month=month)
    assert month_data.value_jp == sep_month_days*96    
    year_data = YearData.objects.filter(year__year_number=2021)[0]
    assert year_data.value_pp == sep_month_days*96       
    # verify that previous year is intact
    year_data = YearData.objects.filter(year__year_number=2020)[0]       
    assert year_data.value_pp == (jan_month_days*96+feb_month_days*96+mar_month_days*96)
    # test that state is updated
    state = ImportState.load()
    assert state.current_month_number == 9
    assert state.current_year_number == 2021
    #test year change and week 53
    start_time = dateutil.parser.parse("2020-12-26 00:00:00")
    end_time = dateutil.parser.parse("2021-01-11 23:45:45")
    out = import_command(test_mode=(start_time, end_time))
    weeks = Week.objects.filter(week_number=53, years__year_number=2020)
    assert len(weeks) == num_stations
    assert weeks[0].days.all().count() == 7
    weeks = Week.objects.filter(week_number=53, years__year_number=2021)
    assert len(weeks) == num_stations
    assert weeks[0].days.all().count() == 7
    weeks =Week.objects.filter(week_number=1, years__year_number=2021)
    assert len(weeks), num_stations
    assert weeks[0].days.all().count() == 7
   

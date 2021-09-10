from datetime import datetime
import dateutil.parser
import pytest
from rest_framework.test import APIClient

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

TEST_TIME = dateutil.parser.parse("2020-01-01 00:00:00")

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
@pytest.fixture
def station():
    station = Station.objects.create(
        name="Auransilta",
        geom="POINT(60.4487578455581 22.269454227550053)"
    )
    return station

@pytest.mark.django_db
@pytest.fixture
def year(station):
    year = Year.objects.create(
        station=station,
        year_number=TEST_TIME.year
    )
    return year

@pytest.mark.django_db
@pytest.fixture
def month(station, year):
    month = Month.objects.create(
        station=station,
        year=year,
        month_number=TEST_TIME.month
    )
    return month

@pytest.mark.django_db
@pytest.fixture
def week(station, year):
    week_number = int(TEST_TIME.strftime("%-V"))
    print("WEEK NUMBER ", week_number)
    week = Week.objects.create(
        station=station,       
        week_number=week_number
    )
    week.years.add(year)
    return week

@pytest.mark.django_db
@pytest.fixture
def day(station, year, month, week):
    day = Day.objects.create(
        station=station,
        date=TEST_TIME,
        weekday_number=TEST_TIME.weekday(),
        week=week,
        month=month,
        year=year, 
    )
    return day

@pytest.mark.django_db
@pytest.fixture
def hour_data(station, day):
    hour_data = HourData.objects.create(
        station=station,
        day=day,
        values_ak=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]
    )
    return hour_data

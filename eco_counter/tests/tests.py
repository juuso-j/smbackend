import dateutil.parser
from fixtures import *
from datetime import time, timedelta
import pytest
from rest_framework.reverse import reverse


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



@pytest.mark.django_db   
def test_hour(api_client, hour_data):
    url = reverse("hour_data-list")
    response = api_client.get(url)
    assert response.status_code == 200
    for i in range(1, 25):
        assert response.json()["results"][0]["values_ak"][i-1] == i
        print(i)


    
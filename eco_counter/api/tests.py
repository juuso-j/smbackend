from io import StringIO
import dateutil.parser
from datetime import time, timedelta
import redis
from django.test import override_settings, Client
from django.conf import settings
from django.core.management import call_command
from rest_framework.test import APIClient, APITestCase
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

# connect to redis
r = redis.Redis(host="localhost", port="6379", db="0")
@override_settings(CACHES=settings.TEST_CACHES)

class EcoCounterTest(APITestCase):

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

    # @classmethod
    # def setUpClass(cls):
    #     super(EcoCounterTest, cls).setUpClass()
    #     start_time = dateutil.parser.parse("2020-01-01 00:00:00")
    #     end_time = dateutil.parser.parse("2020-02-29 23:45:45")        
    #     out = cls.import_command(cls, test_mode=(start_time, end_time))
    #     cls.client = APIClient()

    def setUp(self):
        self.client = APIClient()
    def test_hour(self):
        response = self.client.get("/api/hour_data/")
        breakpoint()


    
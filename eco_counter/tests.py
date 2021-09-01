from io import StringIO
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

    def test_import(self):
        out = self.import_command("--test-mode 1000")
        print(YearData.objects.get(pk=1).value_jp)
        out = self.import_command("--test-mode 500")
        print(YearData.objects.get(pk=1).value_jp)
        
        breakpoint()

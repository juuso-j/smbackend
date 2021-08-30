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
            "import_volumes",
            *args,
            stdout=out,
            stderr=StringIO(),
            **kwargs,
        )
        return out.getvalue()

    def test_import(self):
        self.import_command()

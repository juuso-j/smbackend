from datetime import datetime
from django.utils.timezone import now
from django.contrib.postgres.fields import ArrayField
from django.contrib.gis.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

START_YEAR = 2020
YEAR_CHOICES = [(r,r) for r in range(2020, datetime.now().year+1)]


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class ImportState(SingletonModel):
    rows_imported = models.PositiveIntegerField(default=0)
    current_year_number = models.PositiveSmallIntegerField(choices=YEAR_CHOICES, default=START_YEAR)
    current_month_number = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)], default=1)


class Location(models.Model):    
    name = models.CharField(max_length=30)
    geom = models.PointField()
    
    def __str__(self):
        return "%s %s" % (self.name, self.geom)


class CounterData(models.Model):
    value_ak = models.PositiveIntegerField(default=0)
    value_ap = models.PositiveIntegerField(default=0)
    value_at = models.PositiveIntegerField(default=0)   
    value_pk = models.PositiveIntegerField(default=0)
    value_pp = models.PositiveIntegerField(default=0)
    value_pt = models.PositiveIntegerField(default=0)  
    value_jk = models.PositiveIntegerField(default=0)
    value_jp = models.PositiveIntegerField(default=0)
    value_jt = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True


class Year(models.Model):
    location = models.ForeignKey("Location", on_delete=models.CASCADE,\
        related_name="years", null=True)
    year_number = models.PositiveSmallIntegerField(choices=YEAR_CHOICES, default=datetime.now().year)
    

class Month(models.Model):
    location = models.ForeignKey("Location", on_delete=models.CASCADE,\
        related_name="months", null=True)
    #year = models.PositiveSmallIntegerField(choices=YEAR_CHOICES, default=datetime.now().year)
    year = models.ForeignKey("Year", on_delete=models.CASCADE, related_name="months")
    month_number = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)], default=1)


class Week(models.Model):
    location = models.ForeignKey("Location", on_delete=models.CASCADE,\
        related_name="weeks")
    week_number = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(53)])
    year = models.ForeignKey("Year", on_delete=models.CASCADE, related_name="weeks", null=True)
    month = models.ForeignKey("Month", on_delete=models.CASCADE, related_name="weeks", null=True)
  

class YearData(CounterData):
    location = models.ForeignKey("Location", on_delete=models.CASCADE,\
        related_name="year_data", null=True)    
    year = models.ForeignKey("Year", on_delete=models.CASCADE, related_name="year_data", null=True)


class MonthData(CounterData):
    location = models.ForeignKey("Location", on_delete=models.CASCADE,\
        related_name="month_data", null=True)    
    month = models.ForeignKey("Month", on_delete=models.CASCADE, related_name="month_data", null=True)
    year = models.ForeignKey("Year", on_delete=models.CASCADE, related_name="month_data", null=True)


class WeekData(CounterData):
    location = models.ForeignKey("Location", on_delete=models.CASCADE,\
        related_name="week_data", null=True)    
    week = models.ForeignKey("Week", on_delete=models.CASCADE, related_name="week_data", null=True)
    month = models.ForeignKey("Month", on_delete=models.CASCADE, related_name="week_data", null=True)


class WeekDay(CounterData):
    location = models.ForeignKey("Location", on_delete=models.CASCADE,\
        related_name="weekdays", null=True)      
    week = models.ForeignKey("Week", on_delete=models.CASCADE, related_name="week_days", null=True)
    date = models.DateField(default=now)
    day_number = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(7)], default=1)
 

class Day(models.Model):    
    location = models.ForeignKey("Location", on_delete=models.CASCADE,\
        related_name="days")
    week = models.ForeignKey("Week", on_delete=models.CASCADE, related_name="days", null=True)
    month = models.ForeignKey("Month", on_delete=models.CASCADE, related_name="days", null=True)
    date = models.DateField(default=now)
    day_number = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(7)], default=1)
    values_ak = ArrayField(models.PositiveSmallIntegerField(), default=list)
    values_ap = ArrayField(models.PositiveSmallIntegerField(), default=list)
    values_at = ArrayField(models.PositiveSmallIntegerField(), default=list)    
    values_pk = ArrayField(models.PositiveSmallIntegerField(), default=list)
    values_pp = ArrayField(models.PositiveSmallIntegerField(), default=list)
    values_pt = ArrayField(models.PositiveSmallIntegerField(), default=list)    
    values_jk = ArrayField(models.PositiveSmallIntegerField(), default=list)
    values_jp = ArrayField(models.PositiveSmallIntegerField(), default=list)
    values_jt = ArrayField(models.PositiveSmallIntegerField(), default=list)


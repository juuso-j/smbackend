from datetime import datetime
from django.utils.timezone import now
from django.contrib.postgres.fields import ArrayField
from django.contrib.gis.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.fields import related


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
    # default is set to 1, 0
    rows_imported = models.IntegerField(default=0)



class Location(models.Model):    
    name = models.CharField(max_length=30)
    geom = models.PointField()
    
    def __str__(self):
        return "%s %s" % (self.name, self.geom)

YEAR_CHOICES = [(r,r) for r in range(2019, datetime.now().year+1)]

# store cumulative sum of months
class Year(models.Model):
    year = models.IntegerField(choices=YEAR_CHOICES, default=datetime.now().year)
    pass

class Month(models.Model):
    location = models.ForeignKey("Location", on_delete=models.CASCADE,\
        related_name="months", null=True)
    year = models.IntegerField(choices=YEAR_CHOICES, default=datetime.now().year)
    month_number = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)], default=1)


class Week(models.Model):
    location = models.ForeignKey("Location", on_delete=models.CASCADE,\
        related_name="weeks")
    week_number = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(53)])
    month = models.ForeignKey("Month", on_delete=models.CASCADE, related_name="weeks", null=True)
    year = models.IntegerField(choices=YEAR_CHOICES, default=datetime.now().year)

class WeekDay(models.Model):
    week = models.ForeignKey("Week", on_delete=models.CASCADE, related_name="week_day", null=True)

class Day(models.Model):
    location = models.ForeignKey("Location", on_delete=models.CASCADE,\
        related_name="days")
    week = models.ForeignKey("Week", on_delete=models.CASCADE, related_name="days", null=True)
    month = models.ForeignKey("Month", on_delete=models.CASCADE, related_name="days", null=True)
    date = models.DateField(default=now().date())
    values_ak = ArrayField(models.IntegerField(), default=list)
    values_ap = ArrayField(models.IntegerField(), default=list)
    values_at = ArrayField(models.IntegerField(), default=list)    
    values_pk = ArrayField(models.IntegerField(), default=list)
    values_pp = ArrayField(models.IntegerField(), default=list)
    values_pt = ArrayField(models.IntegerField(), default=list)    
    values_jk = ArrayField(models.IntegerField(), default=list)
    values_jp = ArrayField(models.IntegerField(), default=list)
    values_jt = ArrayField(models.IntegerField(), default=list)


#from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.gis.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


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


# class Observation_OLD(models.Model):
#     location = models.ForeignKey("Location", on_delete=models.CASCADE,\
#          related_name="observations")
#     time = models.DateTimeField()
#     #value = models.ArrayField(models.IntegerField())
#     type = models.CharField(max_length=5)

#     class Meta:
#         ordering = ["-time"]

#     def __str__(self):
#         return "%s %s %s" % (self.time, self.value, self.type)


class Observation(models.Model):
    location = models.ForeignKey("Location", on_delete=models.CASCADE,\
         related_name="observations")
    time = models.DateTimeField()
   
    value = models.IntegerField(null=True)
    type = models.CharField(max_length=5)

    class Meta:
        ordering = ["-time"]

    def __str__(self):
        return "%s %s %s" % (self.time, self.value, self.type)

class Month(models.Model):
    pass


class Week(models.Model):
    location = models.ForeignKey("Location", on_delete=models.CASCADE,\
        related_name="weeks")
    week = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(53)])
    days = models.ForeignKey("Day", on_delete=models.CASCADE, related_name="week")

class Day(models.Model):
    location = models.ForeignKey("Location", on_delete=models.CASCADE,\
        related_name="days")
    time = models.DateTimeField()
    values_ak = ArrayField(models.IntegerField(), size=24)
    values_ap = ArrayField(models.IntegerField(), size=24)
    values_at = ArrayField(models.IntegerField(), size=24)    
    values_pk = ArrayField(models.IntegerField(), size=24)
    values_pp = ArrayField(models.IntegerField(), size=24)
    values_pt = ArrayField(models.IntegerField(), size=24)    
    values_jk = ArrayField(models.IntegerField(), size=24)
    values_jp = ArrayField(models.IntegerField(), size=24)
    values_jt = ArrayField(models.IntegerField(), size=24)

# class Statistic(models.Model):
    
#     TIMESPANS = (
#         ("H", "Hourly"),
#         ("D", "Daily"),
#         ("W", "Weekly"),
#         ("M", "Monthly"),
#         ("Y", "Yearly"),
#     )
#     location = models.ForeignKey("Location", on_delete=models.CASCADE,\
#         related_name="statistics")
#     timespan = models.CharField(max_length=1, choices=TIMESPANS) # TODO add hourly, daily, weekly etc
#     values_ak = ArrayField(models.IntegerField())
#     values_ap = ArrayField(models.IntegerField())
#     values_at = ArrayField(models.IntegerField())    
#     values_pk = ArrayField(models.IntegerField())
#     values_pp = ArrayField(models.IntegerField())
#     values_pt = ArrayField(models.IntegerField())    
#     values_jk = ArrayField(models.IntegerField())
#     values_jp = ArrayField(models.IntegerField())
#     values_jt = ArrayField(models.IntegerField())
    
#from django.db import models
from django.contrib.gis.db import models

class Location(models.Model):    
    name = models.CharField(max_length=30)
    geom = models.PointField()
    
    def __str__(self):
        return "%s %s" % (self.name, self.geom)

class Observation(models.Model):
    location = models.ForeignKey("Location", on_delete=models.CASCADE,\
         related_name="observations")
    time = models.DateTimeField()
    value = models.IntegerField()
    type = models.CharField(max_length=5)

    class Meta:
        ordering = ["-time"]

    def __str__(self):
        return "%s %s %s" % (self.time, self.value, self.type)
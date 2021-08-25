from rest_framework import serializers
from .models import Day, Location

class DaySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Day
        fields = "__all__"


class LocationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Location
        fields = "__all__"
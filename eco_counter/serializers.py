from rest_framework import serializers
from .models import Day, Location, Week, WeekDay

class DaySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Day
        fields = "__all__"


class LocationSerializer(serializers.ModelSerializer):

    lat = serializers.SerializerMethodField(read_only=True)
    lon = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Location
        fields = [
            "id",
            "name",
            "geom",
            "lat",
            "lon",
            ]

    def get_lat(self, obj):
        return obj.geom.y

    def get_lon(self, obj):
        return obj.geom.x


class WeekDaySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = WeekDay
        fields = "__all__"


class WeekSerializer(serializers.ModelSerializer):

    class Meta:
        model = Week
        fields = "__all__"
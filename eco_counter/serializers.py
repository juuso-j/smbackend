from rest_framework import serializers
from .models import (
    Day, 
    Location, 
    Week, 
    WeekDay, 
    WeekData,
    Month,
    MonthData)

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
        return obj.geom.x

    def get_lon(self, obj):
        return obj.geom.y


class WeekDaySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = WeekDay
        fields = "__all__"


class WeekBaseSerializer(serializers.ModelSerializer):

   class Meta:
        model = Week
        fields = [
            "id",
            "location",
            "week_number",
            "year",
        ]


class WeekSerializer(WeekBaseSerializer):
    week_days = WeekDaySerializer(many=True, read_only=True)
    num_days = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Week
        fields = [           
            "num_days",
            "week_days",
        ]
    
    def get_num_days(self, obj):
        return len(obj.week_days.values_list())



class WeekDataSerializer(serializers.ModelSerializer):
    #week = serializers.PrimaryKeyRelatedField(many=False, queryset=Week.objects.all())
    week_info = WeekBaseSerializer(source="week")
    class Meta:
        
        model = WeekData
        fields = [
            "id",
            "location",
            #"week",
            "week_info",
            "value_ak",
            "value_ap",
            "value_at",
            "value_pk",
            "value_pp",
            "value_pt",
            "value_jk",
            "value_jp",
            "value_jt",          
            
        ]

    
class MonthSerializer(serializers.ModelSerializer):

    class Meta:
        model = Month
        fields = "__all__"


class MonthDataSerializer(serializers.ModelSerializer):
    month_info = MonthSerializer(source="month")
    class Meta:
        
        model = MonthData
        fields = [
            "id",
            "location",
            "month_info",
            "value_ak",
            "value_ap",
            "value_at",
            "value_pk",
            "value_pp",
            "value_pt",
            "value_jk",
            "value_jp",
            "value_jt",          
            
        ]


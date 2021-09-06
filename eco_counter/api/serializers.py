from rest_framework import serializers
from ..models import (
    Station,
    HourData, 
    DayData,
    WeekData,
    MonthData,
    YearData,
    Day,
    Week,
    Month, 
    Year
)

class StationSerializer(serializers.ModelSerializer):

    lat = serializers.SerializerMethodField(read_only=True)
    lon = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Station
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


class HourDataSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = HourData
        fields = "__all__"


class DayDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = DayData
        field = "__all__"


class DaySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Day
        fields = "__all__"


class WeekBaseSerializer(serializers.ModelSerializer):

   class Meta:
        model = Week
        fields = [
            "id",
            "station",
            "week_number",
            #"year__year_number",
        ]


class WeekSerializer(WeekBaseSerializer):
    days = DaySerializer(many=True, read_only=True)
    num_days = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Week
        fields = [           
            "num_days",
            "days",
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
            "station",
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


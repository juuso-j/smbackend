# from rest_framework import serializers
# from rest_framework_gis.serializers import GeoFeatureModelSerializer
# from ..models import (
#     Unit,
#     ContentTypes,
#     Geometry,
#     ChargingStationContent,
#     GasFillingStationContent
# )








# class GasFillingStationContentSerializer(serializers.ModelSerializer):
    
#     class Meta:
#         model = GasFillingStationContent
#         fields = [
#             "name",
#             "address",
#             "operator",
#             "lng_cng",            
#             ]



# # class UnitSerializerOLD(serializers.ModelSerializer):
   
# #     geometries = serializers.StringRelatedField(many=True)
# #     content_type = ContentTypesSerializer()
# #     content = serializers.SerializerMethodField()

# #     class Meta:
# #         model = Unit
# #         fields = [
# #             "created_time",
# #             "is_active",
# #             "content_type",
# #             "content",
# #             "geometries",
# #         ]
# #     def get_content(self, obj):
# #         content = None
# #         if obj.content_type.short_name == ContentTypes.GAS_FILLING_STATION:
# #             content = obj.gas_filling_station_content           
# #         elif obj.content_type.short_name == ContentTypes.CHARGING_STATION:
# #             content = obj.charging_station_content 

# #         ser_data = django_serializers.serialize("json",[content,])
# #         return json.loads(ser_data) 



# class GeometrySerializer(GeoFeatureModelSerializer):
#     unit = UnitInfoSerializer()
#     class Meta:
#         model = Geometry
#         geo_field = "geometry"
#         fields = [
#             "geometry",
#             "unit",
#         ]
 





# class GasFillingStationSerializer(GeoFeatureModelSerializer):
#     unit = UnitInfoSerializer()
#     gas_filling_station_content = GasFillingStationContentSerializer(many=False, read_only=True, source="unit.gas_filling_station_content")
#     class Meta:
#         model = Geometry
#         geo_field = "geometry"
#         fields = [
#             "geometry",
#             "unit",
#             "gas_filling_station_content",
#         ]


   
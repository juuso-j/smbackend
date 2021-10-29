import logging

from django.contrib.gis.geos import GEOSGeometry, Point, LineString
from django.core.management import BaseCommand
from django import db
from django.conf import settings

from data_view.models import (
    Unit,
    UnitGroup,
    ContentTypes,
    GroupTypes,
    StatueContent,
    WalkingRouteContent

)
@db.transaction.atomic    
def save_to_database():
    GroupTypes.objects.all().delete()
    for i in range(1,2):
        group_type, created = GroupTypes.objects.get_or_create(
            type_name="KKR",
            name="KulttuuriKävelyReitti",
        
        )
        unit_group = UnitGroup.objects.get_or_create(
            group_type=group_type,
            name="Paavo Nurmi mockup reitti",
            description="Reitti jossa Paavo Nurmen patsas."        
        )[0]

        statue_type = ContentTypes.objects.get_or_create(
            type_name=ContentTypes.STATUE            
        )[0]
        walking_route_type = ContentTypes.objects.get_or_create(
            type_name=ContentTypes.WALKING_ROUTE
        )[0]
        point = Point(236562.14196270588+i*100, 6704811.571559942+i*100, srid=settings.DEFAULT_SRID)
        linestring = LineString(
            (236562.14196270588+i*100, 6704811.571559942+i*100),
            (237562.14196270588+i*100, 6714811.571559942+i*100),
            (237962.14196270588+i*100, 6744811.571559942+i*100),            
            (234562.14196270588+i*100, 6724811.571559942+i*100),            
            (238562.14196270588+i*100, 6734811.571559942+i*100),         
            
            sird=settings.DEFAULT_SRID)

        statue_unit = Unit.objects.create(
            content_type=statue_type,
            geometry=point,
            unit_group=unit_group,
            name="Paavo Nurmen Patsas",
            address="Itäinen Rantakatu."
        )

        content = StatueContent.objects.create(
            unit=statue_unit,
        )
        # geometry = Geometry.objects.create(
        #     unit=statue_unit,
        #     geometry=point
        # )
        walking_route_unit = Unit.objects.create(
            content_type=walking_route_type,
            geometry=linestring,
            name="Reitin reittidataa.",
            unit_group=unit_group
        )
        content = WalkingRouteContent.objects.create(
            unit=walking_route_unit,
            
        )
    # geometry=Geometry.objects.create(
    #     unit=walking_route_unit,
    #     geometry=linestring
    # )


  

class Command(BaseCommand):


    def handle(self, *args, **options):
        save_to_database()
        pass
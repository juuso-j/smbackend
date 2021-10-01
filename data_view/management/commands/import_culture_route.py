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
    for i in range(5):
        group_type = GroupTypes.objects.get_or_create(
            type_name="FO"+str(i)
        )[0]
        unit_group = UnitGroup.objects.get_or_create(
            group_type=group_type
        )[0]

        statue_type = ContentTypes.objects.get_or_create(
            type_name=ContentTypes.STATUE
        )[0]
        walking_route_type = ContentTypes.objects.get_or_create(
            type_name=ContentTypes.WALKING_ROUTE
        )[0]
        point = Point(236562.14196270588, 6704811.571559942, srid=settings.DEFAULT_SRID)
        linestring = LineString((0, 0), (0, 50), (50, 50), (50, 0), (0, 0), sird=settings.DEFAULT_SRID)

        statue_unit = Unit.objects.create(
            content_type=statue_type,
            geometry=point,
            unit_group=unit_group
        )
        content = StatueContent.objects.create(
            unit=statue_unit,
            name="Paavo nurmi"+str(i)
        )
        # geometry = Geometry.objects.create(
        #     unit=statue_unit,
        #     geometry=point
        # )
        walking_route_unit = Unit.objects.create(
            content_type=walking_route_type,
            geometry=linestring,
            unit_group=unit_group
        )
        content = WalkingRouteContent.objects.create(
            unit=walking_route_unit,
            name="Kulttuuria"+str(i)
        )
    # geometry=Geometry.objects.create(
    #     unit=walking_route_unit,
    #     geometry=linestring
    # )


    breakpoint()

class Command(BaseCommand):


    def handle(self, *args, **options):
        save_to_database()
        pass
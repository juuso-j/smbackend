from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from django.conf import settings

class Command(BaseCommand):
    help = 'Filters geojson file'
    
    def add_arguments(self, parser):        
        parser.add_argument('--location')
        parser.add_argument('--province')

    def handle(self, *args, **options):

        pass
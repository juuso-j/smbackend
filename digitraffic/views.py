import json
from django.core.files import File
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import action
from rest_framework import viewsets
# Create your views here.


class DigiTrafficViewSet(viewsets.ViewSet):

    @action(detail=False)
    def roadworks(self, request):
        filename = settings.MEDIA_ROOT+"/out_location.geojson"
        with open(filename) as f:
            contents = f.read()
        
        print(contents)
        return HttpResponse(contents)

    @action(detail=False)
    def finferries(self, request):
        filename = settings.MEDIA_ROOT+"/finferries.geojson"
        with open(filename) as f:
            contents = f.read()
        
        print(contents)
        return HttpResponse(contents)

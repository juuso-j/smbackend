import requests
from mockup.models import ContentTypes
GEOMETRY_ID = 11 #  11 Varsinaissuomi # 10 Uusim
GEOMETRY_URL = "https://tie.digitraffic.fi/api/v3/data/traffic-messages/area-geometries?id={id}&lastUpdated=false".format(id=GEOMETRY_ID)

def fetch_json(url):
    response = requests.get(url)
    assert response.status_code == 200, "Fetching {} status code: {}".\
            format(url, response.status_code)
    return response.json()


def delete_tables(short_name):
    ContentTypes.objects.filter(short_name=short_name).delete()

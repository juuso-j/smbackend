import requests
from mockup.models import Unit
GEOMETRY_ID = 11 #  11 Varsinaissuomi # 10 Uusim
GEOMETRY_URL = "https://tie.digitraffic.fi/api/v3/data/traffic-messages/area-geometries?id={id}&lastUpdated=false".format(id=GEOMETRY_ID)

def fetch_json(url):
    response = requests.get(url)
    assert response.status_code == 200, "Fetching {} status code: {}".\
            format(url, response.status_code)
    return response.json()


def delete_tables(contet_type):
    Unit.objects.filter(content_type=contet_type).delete()

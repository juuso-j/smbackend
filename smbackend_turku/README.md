# Smbackend Turku

Django app for importing Turku specific data to the service.

## Installation

Add following settings to config_dev.env:

```
ADDITIONAL_INSTALLED_APPS=smbackend_turku
TURKU_API_KEY=secret
ACCESSIBILITY_SYSTEM_ID=secret
```

## Importing data
```
./manage.py geo_import finland --municipalities
./manage.py turku_services_import services accessibility units addresses
./manage.py rebuild_index

```
Importing services...
CALLING URL >>>  https://digiaurajoki.turku.fi:9443/kuntapalvelut/api/v1/palvelut
CALLING URL >>>  https://digiaurajoki.turku.fi:9443/kuntapalvelut/api/v1/palveluluokat
Importing accessibility...
CALLING URL >>>  https://asiointi.hel.fi/kapaesteettomyys/api/v1/accessibility/variables
CALLING URL >>>  https://asiointi.hel.fi/kapaesteettomyys/api/v1/servicepoints/d26b5f28-41c6-40a3-99f9-a1b762cc8191
CALLING URL >>>  https://asiointi.hel.fi/kapaesteettomyys/api/v1/accessibility/servicepoints/d26b5f28-41c6-40a3-99f9-a1b762cc8191/properties
Importing units...
CALLING URL >>>  https://digiaurajoki.turku.fi:9443/kuntapalvelut/api/v1/palvelupisteet
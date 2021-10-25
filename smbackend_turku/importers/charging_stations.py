# import logging
# from .utils import fetch_json, ServiceCodes
# from data_view.importers.charging_stations import(
#     get_json_filtered_by_location,
#     save_to_database,
#     CHARGING_STATIONS_URL

# )

# logger = logging.getLogger("django")

# CHARGING_STATIONS_URL = "https://services1.arcgis.com/rhs5fjYxdOG1Et61/ArcGIS/rest/services/ChargingStations/FeatureServer/0/query?f=json&where=1%20%3D%201%20OR%201%20%3D%201&returnGeometry=true&spatialRel=esriSpatialRelIntersects&outFields=LOCATION_ID%2CNAME%2CADDRESS%2CURL%2COBJECTID%2CTYPE"
# GEOMETRY_ID = 11 #  11 Varsinaissuomi # 10 Uusim

# GEOMETRY_URL = "https://tie.digitraffic.fi/api/v3/data/traffic-messages/area-geometries?id={id}&lastUpdated=false".format(id=GEOMETRY_ID)

# def get_json_filtered_by_location():
#     json_data = fetch_json(CHARGING_STATIONS_URL)
#     geometry_data = fetch_json(GEOMETRY_URL) 
#     polygon = Polygon(geometry_data["features"][0]["geometry"]["coordinates"][0])
#     filtered_data = []
    
#     for data in json_data["features"]:
#         x = data["geometry"].get("x",0)
#         y = data["geometry"].get("y",0)
#         point = Point(x, y)
#         if polygon.intersects(point):
#             filtered_data.append(data)
#     logger.info("Filtered: {} charging stations by location to: {}."\
#         .format(len(json_data["features"]), len(filtered_data)))
        
#     return filtered_data

# def get_charging_station_units(koodi, to_database=False):
#     json_data = fetch_json(CHARGING_STATIONS_URL)
#     filtered_data = get_json_filtered_by_location(json_data)
#     if to_database:
#         save_to_database(filtered_data)

#     out_data = []
#     for i, obj in enumerate(filtered_data):
#         unit = {}      
#         full_address = obj.address.split(",")
#         address = full_address[0]
#         zip_code = full_address[1].split(" ")[1]
#         city = full_address[1].split(" ")[2]
#         unit["koodi"] = str(koodi+i)
#         unit["nimi_kieliversiot"] = {}        
#         unit["nimi_kieliversiot"]["fi"] = obj.name
#         unit["fyysinenPaikka"] = {}
#         unit["fyysinenPaikka"]["leveysaste"] = obj.y; 
#         unit["fyysinenPaikka"]["pituusaste"] = obj.x; 
#         unit["fyysinenPaikka"]["koordinaattiAsettuKasin"] = "True"
#         unit["fyysinenPaikka"]["osoitteet"] = []
#         osoite = {}
#         osoite["katuosoite_fi"] = address
#         osoite["katuosoite_sv"] = address
#         osoite["katuosoite_en"] = address
#         osoite["postinumero"] = zip_code
#         osoite["postitoimipaikka_fi"] = city
#         osoite["postitoimipaikka_sv"] = city
#         osoite["postitoimipaikka_en"] = city
#         unit["fyysinenPaikka"]["osoitteet"].append(osoite)
#         unit["tila"] = {}
#         unit["tila"]["koodi"] = "1"
#         unit["tila"]["nimi"] = "Aktiivinen, julkaistu"
#         unit["kuvaus_kieliversiot"] = {}
#         unit["kuvaus_kieliversiot"]["fi"] = obj.charger_type      
#         unit["kuvaus_kieliversiot"]["sv"] = obj.charger_type      
#         unit["kuvaus_kieliversiot"]["en"] = obj.charger_type      
#         extra = {}
#         extra["charger_type"] = obj.charger_type        
#         unit["extra"] = extra

#         unit["palvelutarjoukset"] = []
#         palvelut = {}
#         palvelut["palvelut"] = []
#         palvelu = {}
#         palvelu["koodi"] = ServiceCodes.CHARGING_STATION
#         palvelut["palvelut"].append(palvelu)
#         unit["palvelutarjoukset"].append(palvelut)
#         out_data.append(unit)
#     return out_data

# def get_charging_station_service_node(
#     ylatason_koodi="1_35", # Vapaa aika
#     koodi="1_98", # WHAT?    
#     services=[]
#     ):
    
#     service_node = {}
#     service_node["ylatason_koodi"] = ylatason_koodi
#     service_node["koodi"] = koodi
#     service_node["nimi_kieliversiot"] = {}
#     service_node["nimi_kieliversiot"]["fi"] = "Sähkölatausasemat"
#     service_node["nimi_kieliversiot"]["sv"] = "Laddplatser"
#     service_node["nimi_kieliversiot"]["en"] = "Charging stations"
#     service_node["luokittelutyyppi"] = {}
#     service_node["luokittelutyyppi"]["koodi"] = "1"
#     service_node["luokittelutyyppi"]["nimi"] = "JHS-183"
#     service_node["palvelut"] = []
#     palvelu = {}
#     palvelu["koodi"] = ServiceCodes.CHARGING_STATION # JHS-183 tunnus?
#     service_node["palvelut"].append(palvelu)
#     return [service_node]

# def get_charging_station_service():
#     service = {}
#     service["koodi"] = ServiceCodes.CHARGING_STATION
#     service["tila"] = {}
#     service["tila"]["koodi"] = "1"
#     service["tila"]["nimi"] = "Aktiivinen, julkaistu"
#     service["nimi_kieliversiot"] = {}
#     service["nimi_kieliversiot"]["fi"] = "Sähkölatausasema"
#     return [service]

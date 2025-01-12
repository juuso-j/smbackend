from collections import defaultdict, OrderedDict
from datetime import date, datetime
from functools import lru_cache
import pytz
from django.conf import settings
from django.contrib.gis.gdal import GDAL_VERSION
from django.contrib.gis.geos import Point, Polygon
from django.utils import formats, translation
from django.utils.dateparse import parse_date
from munigeo.importer.sync import ModelSyncher
from munigeo.models import Municipality
from data_view.importers.gas_filling_station import (
    get_filtered_gas_filling_station_objects  
)
from services.management.commands.services_import.services import (
    remove_empty_service_nodes,
    update_service_node_counts,
)
from services.models import (
    Service,
    ServiceNode,
    Unit,
    UnitAccessibilityShortcomings,
    UnitConnection,
    UnitIdentifier,
    UnitServiceDetails,
)
from services.utils import AccessibilityShortcomingCalculator
from smbackend_turku.importers.utils import (
    get_localized_value,
    get_turku_resource,
    get_weekday_str,
    set_syncher_object_field,
    set_syncher_tku_translated_field,
)
from smbackend_turku.importers.stations import (
    GasFillingStationImporter,
    ChargingStationImporter,   
)


UTC_TIMEZONE = pytz.timezone("UTC")

ROOT_FIELD_MAPPING = {
    "nimi_kieliversiot": "name",
    "kuvaus_kieliversiot": "description",
    "sahkoposti": "email",
}

EXTRA_INFO_FIELD_MAPPING = {
    "3": {"kuvaus_kieliversiot": "www"},
    "6": {"kuvaus_kieliversiot": "www"},
    "5": {"nimi": "picture_url"},
}

SERVICE_TRANSLATIONS = {
    "fi": "<b>Palvelut</b>",
    "sv": "<b>Tjänster</b>",
    "en": "<b>Services</b>",
}

# Opening hours types
NORMAL = "normaali"
NORMAL_EXTRA = "normaali extra"
SPECIAL = "erityinen"
EXCEPTION_OPEN = "poikkeus avoinna"
EXCEPTION_CLOSED = "poikkeus suljettu"
EXCEPTION = "poikkeus"  # extra type that represents both exception types

OPEN_STR = {
    "fi": "Avoinna",
    "sv": "Öppna",
    "en": "Open",
}

CLOSED_STR = {
    "fi": "suljettu",
    "sv": "stängt",
    "en": "closed",
}

SPECIAL_STR = {
    "fi": "Erityisaukiolo",
    "sv": "Specielt",
    "en": "Special opening hours",
}

# UnitConnection section types
PHONE_OR_EMAIL_SECTION_TYPE = 1
OPENING_HOURS_SECTION_TYPE = 5

LANGUAGES = ("fi", "sv", "en")

SOURCE_DATA_SRID = 4326

# Use implicit bounding box with GDAL 3 and greater, because axis order has been changed:
# https://trac.osgeo.org/gdal/wiki/rfc73_proj6_wkt2_srsbarn#Axisorderissues
if GDAL_VERSION[0] >= 3 and settings.BOUNDING_BOX_WSG84:
    BOUNDING_BOX = Polygon.from_bbox(settings.BOUNDING_BOX_WSG84)
    BOUNDING_BOX.srid = SOURCE_DATA_SRID
else:
    BOUNDING_BOX = Polygon.from_bbox(settings.BOUNDING_BOX)
    BOUNDING_BOX.srid = settings.DEFAULT_SRID
    BOUNDING_BOX.transform(SOURCE_DATA_SRID)


@lru_cache(None)
def get_municipality(name):
    try:
        return Municipality.objects.get(name=name)
    except Municipality.DoesNotExist:
        return None

def create_language_dict(value):
    lang_dict = {}
    for lang in LANGUAGES:
        lang_dict[lang] = value
    return lang_dict

def get_gas_filling_units(id_off):
    units = []
    objects = get_filtered_gas_filling_station_objects()

    for i, object in enumerate(objects):    
        unit = {}
        unit["koodi"] = str(id_off+i)
        unit["nimi_kieliversiot"] = {}
        unit["nimi_kieliversiot"] = create_language_dict(object.name)
        unit["fyysinenPaikka"] = {}
        unit["fyysinenPaikka"]["leveysaste"] = object.point.y
        unit["fyysinenPaikka"]["pituusaste"] = object.point.x
        unit["fyysinenPaikka"]["koordinaattiAsettuKasin"] = "True"
        unit["fyysinenPaikka"]["osoitteet"] = []
        osoite = {}
        osoite["katuosoite_fi"] = object.address
        osoite["katuosoite_sv"] = object.address
        osoite["katuosoite_en"] = object.address
        osoite["postinumero"] = object.zip_code
        osoite["postitoimipaikka_fi"] = object.city
        osoite["postitoimipaikka_sv"] = object.city
        osoite["postitoimipaikka_en"] = object.city
        unit["fyysinenPaikka"]["osoitteet"].append(osoite)
        unit["tila"] = {}
        unit["tila"]["koodi"] = "1"
        unit["tila"]["nimi"] = "Aktiivinen, julkaistu"
        unit["kuvaus_kieliversiot"] = {}
        description = object.operator + " " + object.lng_cng
        unit["kuvaus_kieliversiot"] = create_language_dict(description)
        extra = {}
        extra["operator"] = object.operator
        extra["lng_cng"] = object.lng_cng        
        unit["extra"] = extra
        units.append(unit)

    return units


class UnitImporter:
    unitsyncher = ModelSyncher(Unit.objects.all(), lambda obj: obj.id)  

    def __init__(self, logger=None, importer=None, test=False):
        self.logger = logger
        self.importer = importer
        self.test = test

    def import_units(self):
        #import_gas()
        units = get_turku_resource("palvelupisteet", "palvelupisteet")
        #gas_units = get_gas_filling_units(self._get_next_koodi(units))
        #units += gas_units
        #breakpoint()
        #if not self.test:

            # units += get_gas_filling_station_units(
            #     self._get_next_koodi(units), 
            #     to_database=True
            # )  
            #units += get_charging_station_units(self._get_next_koodi(units))        
        # units = get_gas_filling_station_units(10000)        
        
        for unit in units:
            self._handle_unit(unit)
    

        self._handle_external_units(GasFillingStationImporter)
        self._handle_external_units(ChargingStationImporter)
        self.unitsyncher.finish()
        
        update_service_node_counts()       
        remove_empty_service_nodes(self.logger)

    def _get_next_koodi(self, units):
        """
        Return t
        """
        return int(units[-1]["koodi"])+1


    def _handle_external_units(self, importer):
        service = None
        try:
            service = Service.objects.get(name=importer.SERVICE_NAME)
        except:
            pass        
        if service:
            units_qs = Unit.objects.filter(services__id=service.id) 
            for unit in units_qs.all():
                synch_unit = self.unitsyncher.get(unit.id)
                self.unitsyncher.mark(synch_unit)
                
       

    def _handle_unit(self, unit_data):
        unit_id = int(unit_data["koodi"])
        state = unit_data["tila"].get("koodi")

        if state != "1":
            self.logger.debug(
                'Skipping service point "{}" state "{}".'.format(unit_id, state)
            )
            return

        obj = self.unitsyncher.get(unit_id)
        if not obj:
            obj = Unit(id=unit_id)
            obj._changed = True

        self._handle_root_fields(obj, unit_data)
        self._handle_location(obj, unit_data)
        self._handle_extra_info(obj, unit_data)
        self._handle_extra_data(obj, unit_data)
        self._handle_ptv_id(obj, unit_data)
        self._handle_service_descriptions(obj, unit_data)
        self._save_object(obj)

        self._handle_opening_hours(obj, unit_data)
        self._handle_email_and_phone_numbers(obj, unit_data)
        self._handle_services_and_service_nodes(obj, unit_data)
        self._handle_accessibility_shortcomings(obj)
        self._save_object(obj)

        self.unitsyncher.mark(obj)

    def _save_object(self, obj):
        if obj._changed:
            obj.last_modified_time = datetime.now(UTC_TIMEZONE)
            obj.save()
            if self.importer:
                self.importer.services_changed = True

    def _handle_root_fields(self, obj, unit_data):
        self._update_fields(obj, unit_data, ROOT_FIELD_MAPPING)

    def _handle_location(self, obj, unit_data):
        location_data = unit_data.get("fyysinenPaikka")
        location = None

        if location_data:
            latitude = location_data.get("leveysaste")
            longitude = location_data.get("pituusaste")

            if latitude and longitude:
                point = Point(float(longitude), float(latitude), srid=SOURCE_DATA_SRID)

                if point.within(BOUNDING_BOX):
                    point.transform(settings.DEFAULT_SRID)
                    location = point

        set_syncher_object_field(obj, "location", location)

        if not location_data:
            return

        address_data_list = location_data.get("osoitteet")

        if address_data_list:
            # TODO what if there are multiple addresses
            address_data = address_data_list[0]

            full_postal_address = {}
            street = {"fi": address_data.get("katuosoite_fi")}

            zip = address_data.get("postinumero")
            post_office_fi = address_data.get("postitoimipaikka_fi")
            full_postal_address["fi"] = "{} {} {}".format(
                street["fi"], zip, post_office_fi
            )

            for language in ("sv", "en"):
                street[language] = (
                    address_data.get("katuosoite_{}".format(language)) or street["fi"]
                )
                post_office = (
                    address_data.get("postitoimipaikka_{}".format(language))
                    or post_office_fi
                )
                full_postal_address[language] = "{} {} {}".format(
                    street[language], zip, post_office
                )

            set_syncher_tku_translated_field(
                obj, "address_postal_full", full_postal_address
            )
            set_syncher_tku_translated_field(obj, "street_address", street)
            set_syncher_object_field(obj, "address_zip", zip)

            municipality = get_municipality(
                address_data.get("kunta", {}).get("nimi_fi")
            )
            if not municipality:
                municipality = get_municipality(post_office_fi)
            set_syncher_object_field(obj, "municipality", municipality)

    def _handle_extra_info(self, obj, unit_data):
        # TODO handle existing extra data erasing when needed

        location_data = unit_data.get("fyysinenPaikka")
        if not location_data:
            return

        for extra_info_data in location_data.get("lisatiedot", []):
            try:
                koodi = extra_info_data["lisatietotyyppi"].get("koodi")
                field_mapping = EXTRA_INFO_FIELD_MAPPING[koodi]
            except KeyError:
                continue
            self._update_fields(obj, extra_info_data, field_mapping)

    def _handle_extra_data(self, obj, unit_data):
        extra = unit_data.get("extra", None)
        if extra:
            obj.extra = extra
            #obj.save()
            #breakpoint()

        

    def _handle_ptv_id(self, obj, unit_data):
        ptv_id = unit_data.get("ptv_id")

        if ptv_id:
            created, _ = UnitIdentifier.objects.get_or_create(
                namespace="ptv", value=ptv_id, unit=obj
            )
            if created:
                obj._changed = True
        else:
            num_of_deleted, _ = UnitIdentifier.objects.filter(
                namespace="ptv", unit=obj
            ).delete()
            if num_of_deleted:
                obj._changed = True

    def _handle_services_and_service_nodes(self, obj, unit_data):
        old_service_ids = set(obj.services.values_list("id", flat=True))
        old_service_node_ids = set(obj.service_nodes.values_list("id", flat=True))
        obj.services.clear()
        obj.service_nodes.clear()

        for service_offer in unit_data.get("palvelutarjoukset", []):

            for service_data in service_offer.get("palvelut", []):
                service_id = int(service_data.get("koodi"))
                try:
                    service = Service.objects.get(id=service_id)
                except Service.DoesNotExist:
                    # TODO fail the unit node completely here?
                    self.logger.warning(
                        'Service "{}" does not exist!'.format(service_id)
                    )
                    continue

                UnitServiceDetails.objects.get_or_create(unit=obj, service=service)

                service_nodes = ServiceNode.objects.filter(related_services=service)
                obj.service_nodes.add(*service_nodes)
                # if service_id == 9999:
                #     breakpoint()

        new_service_ids = set(obj.services.values_list("id", flat=True))
        new_service_node_ids = set(obj.service_nodes.values_list("id", flat=True))
        if (
            old_service_ids != new_service_ids
            or old_service_node_ids != new_service_node_ids
        ):
            obj._changed = True

        set_syncher_object_field(
            obj,
            "root_service_nodes",
            ",".join(str(x) for x in obj.get_root_service_nodes()),
        )

    def _handle_accessibility_shortcomings(self, obj):
        description, count = AccessibilityShortcomingCalculator().calculate(obj)
        UnitAccessibilityShortcomings.objects.update_or_create(
            unit=obj,
            defaults={
                "accessibility_shortcoming_count": count,
                "accessibility_description": description,
            },
        )

    def _handle_service_descriptions(self, obj, unit_data):
        description_data = unit_data.get("kuvaus_kieliversiot", {})
        descriptions = {
            lang: description_data.get(lang, "") for lang in ("fi", "sv", "en")
        }
        set_syncher_tku_translated_field(obj, "description", descriptions, clean=False)

    def _handle_opening_hours(self, obj, unit_data):
        obj.connections.filter(section_type=OPENING_HOURS_SECTION_TYPE).delete()

        try:
            opening_hours_data = unit_data["fyysinenPaikka"]["aukioloajat"]
        except KeyError:
            self.logger.debug(
                "Cannot find opening hours for unit {}".format(unit_data.get("koodi"))
            )
            return

        # Opening hours data will be stored in a complex structure where opening hours data is
        # first grouped by type and then by Finnish name / title. Inside there each data entry
        # localized name and description list. Example:
        #
        # {
        #   'normaali': {
        #       'Avoinna': (
        #           {'fi': 'Avoinna', 'sv': 'Öppna', 'en': 'Open' },
        #           ['fi': 'ma-pe 10:00-12:00', 'sv': 'mån-fre 10:00-12:00', 'en': 'Mon-Fri 10:00-12:00' }]
        #       ),
        #       '10.10.2020 Avoinna': (
        #           {'fi': ... },
        #           ['fi': ... }
        #       )
        #   },
        #   'erityinen': {
        #       ...
        #   }
        all_opening_hours = defaultdict(OrderedDict)

        for opening_hours_datum in sorted(
            opening_hours_data, key=lambda x: x.get("voimassaoloAlkamishetki")
        ):
            opening_hours_type = opening_hours_datum["aukiolotyyppi"]

            start = parse_date(opening_hours_datum["voimassaoloAlkamishetki"])
            end = parse_date(opening_hours_datum["voimassaoloPaattymishetki"])
            today = date.today()
            if start and start < today and end and end < today:
                continue

            opening_time = self._format_time(opening_hours_datum["avaamisaika"])
            closing_time = self._format_time(opening_hours_datum["sulkemisaika"])

            if (
                not opening_time
                and not closing_time
                and not opening_hours_type == EXCEPTION_CLOSED
            ):
                continue

            names = self._generate_name_for_opening_hours(opening_hours_datum)
            weekday = opening_hours_datum["viikonpaiva"]
            opening_hours_value = {}

            for language in LANGUAGES:
                weekday_str = "–".join(
                    [
                        get_weekday_str(int(wd), language) if wd else ""
                        for wd in weekday.split("-")
                    ]
                )

                if opening_hours_type == EXCEPTION_CLOSED:
                    opening_hours_value[language] = " ".join(
                        (weekday_str, CLOSED_STR[language])
                    )
                else:
                    opening_hours_value[language] = "{} {}–{}".format(
                        weekday_str, opening_time, closing_time
                    )

            # map exception open and exception closed to the same slot to get them
            # sorted by start dates rather than first all open and then all closed
            if EXCEPTION in opening_hours_type:
                opening_hours_type = EXCEPTION

            # append new opening hours name and value to the complex structure
            all_of_type = all_opening_hours.get(opening_hours_type, {})
            data = all_of_type.get(names["fi"], ())
            if not data:
                data = (names, [opening_hours_value])
            else:
                if opening_hours_value not in data[1]:
                    data[1].append(opening_hours_value)
            all_opening_hours[opening_hours_type][names["fi"]] = data

        index = 0

        for opening_hours_type in (NORMAL, NORMAL_EXTRA, SPECIAL, EXCEPTION):
            for description, value in all_opening_hours[opening_hours_type].items():
                names = {}

                for language in LANGUAGES:
                    first_part = value[0][language]
                    if opening_hours_type in (NORMAL, NORMAL_EXTRA, SPECIAL):
                        first_part = "{}".format(first_part)
                    second_part = " ".join(v[language] for v in value[1])
                    names["name_{}".format(language)] = "{} {}".format(
                        first_part, second_part
                    )

                UnitConnection.objects.create(
                    unit=obj,
                    section_type=OPENING_HOURS_SECTION_TYPE,
                    order=index,
                    **names
                )
                index += 1

    def _handle_email_and_phone_numbers(self, obj, unit_data):
        UnitConnection.objects.filter(
            unit=obj, section_type=PHONE_OR_EMAIL_SECTION_TYPE
        ).delete()

        index = 0
        email = unit_data.get("sahkoposti")

        if email:
            UnitConnection.objects.get_or_create(
                unit=obj,
                section_type=PHONE_OR_EMAIL_SECTION_TYPE,
                email=email,
                name_fi="Sähköposti",
                name_sv="E-post",
                name_en="Email",
                order=index,
            )
            index += 1

        phone_number_data = unit_data.get("puhelinnumerot", [])
        if not phone_number_data:
            return

        for phone_number_datum in phone_number_data:
            number_type = phone_number_datum.get("numerotyyppi")
            descriptions = phone_number_datum.get("kuvaus_kieliversiot", {})
            type_names = {
                "fi": number_type.get("teksti_fi"),
                "sv": number_type.get("teksti_sv"),
                "en": number_type.get("teksti_en"),
            }
            names = {
                "name_{}".format(language): get_localized_value(descriptions, language)
                or get_localized_value(type_names, language)  # NOQA
                for language in LANGUAGES
            }

            UnitConnection.objects.get_or_create(
                unit=obj,
                section_type=PHONE_OR_EMAIL_SECTION_TYPE,
                phone=self._generate_phone_number(phone_number_datum),
                order=index,
                **names
            )
            index += 1

    def _generate_phone_number(self, phone_number_datum):
        if not phone_number_datum:
            return ""

        code = phone_number_datum["maakoodi"]
        number = phone_number_datum["numero"]
        return "+{}{}".format(code, number) if code else number

    def _generate_name_for_opening_hours(self, opening_hours_datum):
        opening_hours_type = opening_hours_datum["aukiolotyyppi"]
        names = defaultdict(str)

        for language in LANGUAGES:
            names[language] = get_localized_value(
                opening_hours_datum.get("kuvaus_kieliversiot", {}), language
            )  # NOQA

        for language in LANGUAGES:
            if not names[language]:
                if opening_hours_type == SPECIAL:
                    names[language] = SPECIAL_STR[language]
                elif opening_hours_type in (NORMAL, NORMAL_EXTRA):
                    names[language] = OPEN_STR[language]

        start = parse_date(opening_hours_datum["voimassaoloAlkamishetki"])
        end = parse_date(opening_hours_datum["voimassaoloPaattymishetki"])

        if not start and not end:
            return names

        # if end < start assume it means just one day (start)
        if end and start and end < start:
            end = start

        for language in LANGUAGES:
            with translation.override(language):
                start_str = (
                    formats.date_format(start, format="SHORT_DATE_FORMAT")
                    if start
                    else None
                )
                end_str = (
                    formats.date_format(end, format="SHORT_DATE_FORMAT")
                    if end
                    else None
                )

            # shorten start date string if it has the same year and/or month as end date,
            # for example 5.7.2018 - 9.7.2018 becomes 5. - 9.7.2018
            if (
                language in ("fi", "sv")
                and start_str
                and end_str
                and start_str != end_str
            ):
                original_start_str = start_str
                if start.year == end.year:
                    if start.month == end.month:
                        start_str = "{}.".format(original_start_str.split(".")[0])
                    else:
                        start_str = ".".join(original_start_str.split(".")[:-1])

            if start and end:
                dates = (
                    "{}–{}".format(start_str, end_str) if start != end else start_str
                )
            else:
                dates = start_str or end_str
            names[language] = (
                "{} {}".format(dates, names[language]) if names[language] else dates
            )

        return names

    def _format_time(self, time_str):
        if not time_str:
            return ""
        parts = time_str.split(":")[:2]
        parts[0] = str(int(parts[0]))
        return ":".join(parts)

    @staticmethod
    def _update_fields(obj, imported_data, field_mapping):
        for data_field, model_field in field_mapping.items():
            value = imported_data.get(data_field)

            if data_field.endswith("_kieliversiot"):
                set_syncher_tku_translated_field(obj, model_field, value)
            else:
                set_syncher_object_field(obj, model_field, value)


def import_units(**kwargs):
    unit_importer = UnitImporter(**kwargs)
    return unit_importer.import_units()

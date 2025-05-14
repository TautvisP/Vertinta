from django.utils.translation import gettext as _

class ObjectTypes:
    LAND_TYPE = _('Sklypas')
    APARTAMENT_TYPE = _('Butas')
    HOUSE_TYPE = _('Namas')
    GARDEN_TYPE = _('Sodas')
    COTTAGE_TYPE = _('Kotedžas')
    OTHER_TYPE = _('Kita')
    STORAGE = _('Sandėliukas')
    ARBOR = _('Pavėsinė')
    GARAGE_TYPE = _('Garažas')

ObjectImages = {
    ObjectTypes.LAND_TYPE: 'land.png',
    ObjectTypes.APARTAMENT_TYPE: 'apartament.png',
    ObjectTypes.HOUSE_TYPE: 'house.png',
    ObjectTypes.GARDEN_TYPE: 'garden.png',
    ObjectTypes.COTTAGE_TYPE: 'kotedzas.png',
    ObjectTypes.OTHER_TYPE: 'other.png'
}

OBJECT_TYPE_CHOICES = (
    (ObjectTypes.LAND_TYPE, ObjectTypes.LAND_TYPE),
    (ObjectTypes.APARTAMENT_TYPE, ObjectTypes.APARTAMENT_TYPE),
    (ObjectTypes.HOUSE_TYPE, ObjectTypes.HOUSE_TYPE),
    (ObjectTypes.GARDEN_TYPE, ObjectTypes.GARDEN_TYPE),
    (ObjectTypes.COTTAGE_TYPE, ObjectTypes.COTTAGE_TYPE),
    (ObjectTypes.OTHER_TYPE, ObjectTypes.OTHER_TYPE)
)

HOUSE_TYPE_1 = _('Namas (gyvenamasis)')
HOUSE_TYPE_2 = _('Namo dalis')
HOUSE_TYPE_3 = _('Sodo namas')
HOUSE_TYPE_4 = _('Sublokuotas namas')
HOUSE_TYPE_5 = _('Sodyba')
HOUSE_TYPE_6 = _('Kita (nukeliamas, projektas, kt.)')

HOUSE_TYPE_CHOICES = [
    (HOUSE_TYPE_1, HOUSE_TYPE_1),
    (HOUSE_TYPE_2, HOUSE_TYPE_2),
    (HOUSE_TYPE_3, HOUSE_TYPE_3),
    (HOUSE_TYPE_4, HOUSE_TYPE_4),
    (HOUSE_TYPE_5, HOUSE_TYPE_5),
    (HOUSE_TYPE_6, HOUSE_TYPE_6),
]

STATUS_CHOICES = (
    (_('Nebaigtas'), _('Nebaigtas')),
    (_('Naujas'), _('Naujas')),
    (_('Patvirtintas'), _('Patvirtintas')),
    (_('Vykdomas'), _('Vykdomas')),
    (_('Įvykdytas'), _('Įvykdytas')),
    (_('Nepateiktas'), _('Nepateiktas')),
)

PRIORITY_CHOICES = (
    (_('Žemas'), _('Žemas')),
    (_('Vidutinis'), _('Vidutinis')),
    (_('Aukštas'), _('Aukštas'))
)

VILNIUS_CITY = _('Vilnius')
KAUNAS_CITY = _('Kaunas')
KLAIPEDA_CITY = _('Klaipėda')
SIAULIAI_CITY = _('Šiauliai')
PANEVEZYS_CITY = _('Panevėžys')
ALYTUS_CITY = _('Alytus')
VILNIUS_DISTRICT = _('Vilniaus r.')
KAUNAS_DISTRICT = _('Kauno r.')
KLAIPEDA_DISTRICT = _('Klaipėdos r.')
SIAULIAI_DISTRICT = _('Šiaulių r.')
PANEVEZYS_DISTRICT = _('Panevėžio r.')
MARIJAMPOLE_CITY = _('Marijampolė')
UTENA_CITY = _('Utena')
TAURAGE_CITY = _('Tauragė')
TELŠIAI_CITY = _('Telšiai')


MUNICIPALITY_CHOICES = [
    (1, VILNIUS_CITY),
    (2, KAUNAS_CITY),
    (3, KLAIPEDA_CITY),
    (4, SIAULIAI_CITY),
    (5, PANEVEZYS_CITY),
    (6, VILNIUS_DISTRICT),
    (7, KAUNAS_DISTRICT),
    (8, KLAIPEDA_DISTRICT),
    (9, SIAULIAI_DISTRICT),
    (10, PANEVEZYS_DISTRICT),
    (11, ALYTUS_CITY),
    (12, MARIJAMPOLE_CITY),
    (13, UTENA_CITY),
    (14, TAURAGE_CITY),
    (15, TELŠIAI_CITY),
]

DECO_TYPE_1 = _('Tinko paviršius tapetuotas')
DECO_TYPE_2 = _('Tinko paviršius tapetuotas/dažytas')
DECO_TYPE_3 = _('Tinko paviršius dažytas')
DECO_TYPE_4 = _('Nėra')
DECO_CHOICES = [
    (DECO_TYPE_1, DECO_TYPE_1),
    (DECO_TYPE_2, DECO_TYPE_2),
    (DECO_TYPE_3, DECO_TYPE_3),
    (DECO_TYPE_4, DECO_TYPE_4),
]

FLOOR_CHOICE1 = _('Betonas')
FLOOR_CHOICE2 = _('Parketas')
FLOOR_CHOICE3 = _('Laminatas')
FLOOR_CHOICE4 = _('Linoleumas')
FLOOR_CHOICE5 = _('Keraminės plytelės')
FLOOR_CHOICE6 = _('Akmens masės plytelės')
FLOOR_CHOICE7 = _('Kiliminė danga')
FLOOR_CHOICE8 = _('Medinės lentos')
FLOOR_CHOICE9 = _('Vinilinė danga')

FLOOR_CHOICES = [
    (FLOOR_CHOICE1, FLOOR_CHOICE1),
    (FLOOR_CHOICE2, FLOOR_CHOICE2),
    (FLOOR_CHOICE3, FLOOR_CHOICE3),
    (FLOOR_CHOICE4, FLOOR_CHOICE4),
    (FLOOR_CHOICE5, FLOOR_CHOICE5),
    (FLOOR_CHOICE6, FLOOR_CHOICE6),
    (FLOOR_CHOICE7, FLOOR_CHOICE7),
    (FLOOR_CHOICE8, FLOOR_CHOICE8),
    (FLOOR_CHOICE9, FLOOR_CHOICE9),
]


FLOOR_COUNT_CHOICE1 = _('1')
FLOOR_COUNT_CHOICE2 = _('2')
FLOOR_COUNT_CHOICE3 = _('Daugiau nei 2')

FLOOR_COUNT_CHOICES = [
    (FLOOR_COUNT_CHOICE1, FLOOR_COUNT_CHOICE1),
    (FLOOR_COUNT_CHOICE2, FLOOR_COUNT_CHOICE2),
    (FLOOR_COUNT_CHOICE3, FLOOR_COUNT_CHOICE3),
]



OUTDOOR_DECO_1 = _('Medinės lentos')
OUTDOOR_DECO_2 = _('Tinkas')
OUTDOOR_DECO_CHOICES = [
    (OUTDOOR_DECO_1, OUTDOOR_DECO_1),
    (OUTDOOR_DECO_2, OUTDOOR_DECO_2),
]

FOUNDATION_TYPE_1 = _('Gręžtiniai')
FOUNDATION_TYPE_2 = _('Monolitiniai')
FOUNDATION_TYPE_3 = _('Juostiniai')
FOUNDATION_TYPE_4 = _('Plokštuminiai')
FOUNDATION_TYPE_5 = _('Iš blokų')
FOUNDATION_TYPE_6 = _('Poliniai')

FOUNDATION_CHOICES = [
    (FOUNDATION_TYPE_1,  _('Gręžtiniai')),
    (FOUNDATION_TYPE_2, _('Monolitiniai')),
    (FOUNDATION_TYPE_3, _('Juostiniai')),
    (FOUNDATION_TYPE_4, _('Plokštuminiai')),
    (FOUNDATION_TYPE_5, _('Iš blokų')),
    (FOUNDATION_TYPE_6, _('Poliniai')),
]

WALLS_TYPE_1 = _('Blokelių mūras')
WALLS_TYPE_2 = _('Medis')
WALLS_TYPE_3 = _('Betonas')
WALLS_TYPE_4 = _('Plytos')
WALLS_TYPE_5 = _('Keramikiniai blokeliai')
WALLS_TYPE_6 = _('Silikatiniai blokeliai')
WALLS_TYPE_7 = _('Akytojo betono blokeliai')
WALLS_TYPE_8 = _('Keramzitbetonio blokeliai')
WALLS_TYPE_9 = _('Karkasinės')

WALLS_CHOICES = [
    (WALLS_TYPE_1, _('Blokelių mūras')),
    (WALLS_TYPE_2, _('Medis')),
    (WALLS_TYPE_3, _('Betonas')),
    (WALLS_TYPE_4, _('Plytos')),
    (WALLS_TYPE_5, _('Keramikiniai blokeliai')),
    (WALLS_TYPE_6, _('Silikatiniai blokeliai')),
    (WALLS_TYPE_7, _('Akytojo betono blokeliai')),
    (WALLS_TYPE_8, _('Keramzitbetonio blokeliai')),
    (WALLS_TYPE_8, _('Karkasinės')),
]


BUILDING_TYPE_1 = _('Mūrinis')
BUILDING_TYPE_2 = _('Blokinis')
BUILDING_TYPE_3 = _('Monolitinis')
BUILDING_TYPE_4 = _('Medinis')
BUILDING_TYPE_5 = _('Karkasinis')
BUILDING_TYPE_6 = _('Rastinis')
BUILDING_TYPE_7 = _('Skydinis')
BUILDING_TYPE_8 = _('Kita')

BUILDING_CHOICES = [
    (BUILDING_TYPE_1, _('Mūrinis')),
    (BUILDING_TYPE_2, _('Blokinis')),
    (BUILDING_TYPE_3, _('Monolitinis')),
    (BUILDING_TYPE_4, _('Medinis')),
    (BUILDING_TYPE_5, _('Karkasinis')),
    (BUILDING_TYPE_6, _('Rastinis')),
    (BUILDING_TYPE_7, _('Skydinis')),
    (BUILDING_TYPE_8, _('Kita')),
]

PARTITION_TYPE_1 = _('Gipso kartono')
PARTITION_TYPE_2 = _('Mūrinė')
PARTITION_TYPE_3 = _('Medinės')

PARTITION_CHOICES = [
    (PARTITION_TYPE_1, _('Gipso kartono')),
    (PARTITION_TYPE_2, _('Mūrinė')),
    (PARTITION_TYPE_3, _('Medinės')),
]


OVERLAY_TYPE_1 = _('Gelžbetonio plokštės')
OVERLAY_TYPE_2 = _('Medinės sijos')
OVERLAY_TYPE_3 = _('Plieninės sijos')

OVERLAY_CHOICES = [
    (OVERLAY_TYPE_1, _('Gelžbetonio plokštės')),
    (OVERLAY_TYPE_2, _('Medinės sijos')),
    (OVERLAY_TYPE_3, _('Plieninės sijos')),
]


ROOF_TYPE_1 = _('Šlaitinis')
ROOF_TYPE_2 = _('Plokščias')
ROOF_TYPE_3 = _('Bituminės čerpės')
ROOF_TYPE_4 = _('Keramikinės čerpės')
ROOF_TYPE_5 = _('Plieninė danga')
ROOF_TYPE_6 = _('Prilydoma danga')
ROOF_TYPE_7 = _('Skalūnas')
ROOF_TYPE_8 = _('Fibrocementinės plokštelės')

ROOF_CHOICES = [
    (ROOF_TYPE_1, _('Šlaitinis')),
    (ROOF_TYPE_2, _('Plokščias')),
    (ROOF_TYPE_3, _('Bituminės čerpės')),
    (ROOF_TYPE_4, _('Keramikinės čerpės')),
    (ROOF_TYPE_5, _('Plieninė danga')),
    (ROOF_TYPE_6, _('Prilydoma danga')),
    (ROOF_TYPE_7, _('Skalūnas')),
    (ROOF_TYPE_8, _('Fibrocementinės plokštelės')),
]


SHED_TYPE_1 = _('Karkasinis')
SHED_TYPE_2 = _('Mūrinis')
SHED_TYPE_3 = _('Metalinė konstrukcija')

SHED_CHOICES = [
    (SHED_TYPE_1, _('Karkasinis')),
    (SHED_TYPE_2, _('Mūrinis')),
    (SHED_TYPE_3, _('Metalinė konstrukcija')),
]


EXIST_TYPE_1 = _('Yra')
EXIST_TYPE_2 = _('Nėra')
EXIST_CHOICES = [
    (EXIST_TYPE_1, _('Yra')),
    (EXIST_TYPE_2, _('Nėra')),
]


BOOL_TYPE_1 = _('Taip')
BOOL_TYPE_2 = _('Ne')
BOOL_CHOICES = [
    (BOOL_TYPE_1, _('Taip')),
    (BOOL_TYPE_2, _('Ne')),
]


GAZEBO_TYPE_1 = _('Medinė')
GAZEBO_TYPE_2 = _('Metalinė')
GAZEBO_TYPE_3 = _('Tentinė')
GAZEBO_CHOICES = [
    (GAZEBO_TYPE_1, _('Medinė')),
    (GAZEBO_TYPE_2, _('Metalinė')),
    (GAZEBO_TYPE_3, _('Tentinė')),
]


ELECTRICITY_TYPE_1 = _('Nėra')
ELECTRICITY_TYPE_2 = _('ESO')
ELECTRICITY_GAS_CHOICES = [
    (ELECTRICITY_TYPE_1, _('Nėra')),
    (ELECTRICITY_TYPE_2, _('ESO')),
]

HEATING_TYPE_1 = _('Centrinis')
HEATING_TYPE_2 = _('Centrinis kolektorinis')
HEATING_TYPE_3 = _('Dujinis')
HEATING_TYPE_4 = _('Elektra')
HEATING_TYPE_5 = _('Aeroterminis')
HEATING_TYPE_6 = _('Geoterminis')
HEATING_TYPE_7 = _('Skystu kuru')
HEATING_TYPE_8 = _('Kietu kuru')
HEATING_TYPE_9 = _('Saules energija')
HEATING_TYPE_10 = _('Kita')

HEATING_CHOICES = [
    (HEATING_TYPE_1, _('Centrinis')),
    (HEATING_TYPE_2, _('Centrinis kolektorinis')),
    (HEATING_TYPE_3, _('Dujinis')),
    (HEATING_TYPE_4, _('Elektra')),
    (HEATING_TYPE_5, _('Aeroterminis')),
    (HEATING_TYPE_6, _('Geoterminis')),
    (HEATING_TYPE_7, _('Skystu kuru')),
    (HEATING_TYPE_8, _('Kietu kuru')),
    (HEATING_TYPE_9, _('Saules energija')),
    (HEATING_TYPE_10, _('Kita')),
]

WATER_SUPPLY_CHOICES = [
    (EXIST_TYPE_1, EXIST_TYPE_1),
    (EXIST_TYPE_2, EXIST_TYPE_2),
]


WASTEWATER_CHOICE1 = _('Komunalinis nuotekų šalinimas')
WASTEWATER_CHOICE2 = _('Individualus nuotekų valymas')

WASTEWATER_CHOICES = [
    (EXIST_TYPE_2, EXIST_TYPE_2),
    (WASTEWATER_CHOICE1, WASTEWATER_CHOICE1),
    (WASTEWATER_CHOICE2, WASTEWATER_CHOICE2),
]


VENTILATION_CHOICES = [
    (EXIST_TYPE_1, EXIST_TYPE_1),
    (EXIST_TYPE_2, EXIST_TYPE_2),
]


SECURITY_CHOICES = [
    (EXIST_TYPE_1, EXIST_TYPE_1),
    (EXIST_TYPE_2, EXIST_TYPE_2),
]


ENERGY_CHOICE1 = _('Nenustatyta')
ENERGY_CHOICE2 = _('A++')
ENERGY_CHOICE3 = _('A+')
ENERGY_CHOICE4 = _('A+')
ENERGY_CHOICE5 = _('A')
ENERGY_CHOICE6 = _('B')
ENERGY_CHOICE7 = _('C')
ENERGY_CHOICE8 = _('D')
ENERGY_CHOICE9 = _('E')
ENERGY_CHOICE10 = _('F')
ENERGY_CHOICE11 = _('G')

ENERGY__EFFICIENCY_CHOICES = [
    (ENERGY_CHOICE1, ENERGY_CHOICE1),
    (ENERGY_CHOICE2, ENERGY_CHOICE2),
    (ENERGY_CHOICE3, ENERGY_CHOICE3),
    (ENERGY_CHOICE4, ENERGY_CHOICE4),
    (ENERGY_CHOICE5, ENERGY_CHOICE5),
    (ENERGY_CHOICE6, ENERGY_CHOICE6),
    (ENERGY_CHOICE7, ENERGY_CHOICE7),
    (ENERGY_CHOICE8, ENERGY_CHOICE8),
    (ENERGY_CHOICE9, ENERGY_CHOICE9),
    (ENERGY_CHOICE10, ENERGY_CHOICE10),
    (ENERGY_CHOICE11, ENERGY_CHOICE11)
]


COOLING_TYPE_1 = _('Oras-oras')
COOLING_TYPE_2 = _('Oras-vanduo')
COOLING_TYPE_3 = _('Geoterminis')

COOLING_CHOICES = [
    (COOLING_TYPE_1, _('Oras-oras')),
    (COOLING_TYPE_2, _('Oras-vanduo')),
    (COOLING_TYPE_3, _('Geoterminis')),
    (EXIST_TYPE_2, EXIST_TYPE_2),
]


WINDOW_TYPE_1 = _('Plastikiniai')
WINDOW_TYPE_2 = _('Aliuminio')
WINDOW_TYPE_3 = _('Mediniai')
WINDOW_TYPE_4 = _('Aliuminio-medienios')

WINDOW_CHOICES = [
    (WINDOW_TYPE_1, _('Plastikiniai')),
    (WINDOW_TYPE_2, _('Aliuminio')),
    (WINDOW_TYPE_3, _('Mediniai')),
    (WINDOW_TYPE_4, _('Aliuminio-medienios')),
]


INNER_DOOR_TYPE_1 = _('Laminuotos')
INNER_DOOR_TYPE_2 = _('Medinės')
INNER_DOOR_TYPE_3 = _('Faneruotos')
INNER_DOOR_TYPE_4 = _('Plastikinės')

INNER_DOOR_CHOICES = [
    (INNER_DOOR_TYPE_1, _('Laminuotos')),
    (INNER_DOOR_TYPE_2, _('Medinės')),
    (INNER_DOOR_TYPE_3, _('Faneruotos')),
    (INNER_DOOR_TYPE_4, _('Plastikinės')),
]


OUTER_DOOR_TYPE_1 = _('Medinės')
OUTER_DOOR_TYPE_2 = _('Šarvo')
OUTER_DOOR_TYPE_3 = _('Plastikinės')
OUTER_DOOR_TYPE_4 = _('Aliuminio')

OUTER_DOOR_CHOICES = [
    (OUTER_DOOR_TYPE_1, _('Medinės')),
    (OUTER_DOOR_TYPE_2, _('Šarvo')),
    (OUTER_DOOR_TYPE_3, _('Plastikinės')),
    (OUTER_DOOR_TYPE_4, _('Aliuminio')),
]

COMERCIAL_TYPE_1 = _('Administracinė')
COMERCIAL_TYPE_2 = _('Prekybos')
COMERCIAL_TYPE_3 = _('Viešbučių')
COMERCIAL_TYPE_4 = _('Paslaugų')
COMERCIAL_TYPE_5 = _('Sandėliavimo')
COMERCIAL_TYPE_6 = _('Gsamybos ir pramonės')
COMERCIAL_TYPE_7 = _('Maitinimo')
COMERCIAL_TYPE_8 = _('Medicinos')
COMERCIAL_TYPE_9 = _('Kita')

COMERCIAL_CHOICES = [
    (COMERCIAL_TYPE_1, _('Administracinė')),
    (COMERCIAL_TYPE_2, _('Prekybos')),
    (COMERCIAL_TYPE_3, _('Viešbučių')),
    (COMERCIAL_TYPE_4, _('Paslaugų')),
    (COMERCIAL_TYPE_5, _('Sandėliavimo')),
    (COMERCIAL_TYPE_6, _('Gsamybos ir pramonės')),
    (COMERCIAL_TYPE_7, _('Maitinimo')),
    (COMERCIAL_TYPE_8, _('Medicinos')),
    (COMERCIAL_TYPE_9, _('Kita')),
]


PURPOSE_TYPE_1 = _('Namų valda')
PURPOSE_TYPE_2 = _('Daugiabučių statyba')
PURPOSE_TYPE_3 = _('Žemės ūkio')
PURPOSE_TYPE_4 = _('Sklypas soduose')
PURPOSE_TYPE_5 = _('Miškų ūkio')
PURPOSE_TYPE_6 = _('Pramonės')
PURPOSE_TYPE_7 = _('Sandėliavimo')
PURPOSE_TYPE_8 = _('Komercinė')
PURPOSE_TYPE_9 = _('Rekreacine')
PURPOSE_TYPE_10 = _('Kita')

LAND_PURPOSE_CHOICES = [
    (PURPOSE_TYPE_1, _('Namų valda')),
    (PURPOSE_TYPE_2, _('Daugiabučių statyba')),
    (PURPOSE_TYPE_3, _('Žemės ūkio')),
    (PURPOSE_TYPE_4, _('Sklypas soduose')),
    (PURPOSE_TYPE_5, _('Miškų ūkio')),
    (PURPOSE_TYPE_6, _('Pramonės')),
    (PURPOSE_TYPE_7, _('Sandėliavimo')),
    (PURPOSE_TYPE_8, _('Komercinė')),
    (PURPOSE_TYPE_9, _('Rekreacine')),
    (PURPOSE_TYPE_10, _('Kita')),
]


EVALUATION_PURPOSE_TYPE_1 = _('Pirkimas')
EVALUATION_PURPOSE_TYPE_2 = _('Pardavimas')
EVALUATION_PURPOSE_TYPE_3 = _('Nuoma')

EVALUATION_PURPOSE_CHOICES = [
    (EVALUATION_PURPOSE_TYPE_1, EVALUATION_PURPOSE_TYPE_1),
    (EVALUATION_PURPOSE_TYPE_2, EVALUATION_PURPOSE_TYPE_2),
    (EVALUATION_PURPOSE_TYPE_3, EVALUATION_PURPOSE_TYPE_3),
]

EVALUATION_CASE_TYPE_1 = _('Pirkimo- pardavimo')
EVALUATION_CASE_TYPE_2 = _('Nuomos')
EVALUATION_CASE_TYPE_3 = _('Kitas')

EVALUATION_CASE_CHOICES = [
    (EVALUATION_CASE_TYPE_1, EVALUATION_CASE_TYPE_1),
    (EVALUATION_CASE_TYPE_2, EVALUATION_CASE_TYPE_2),
    (EVALUATION_CASE_TYPE_3, EVALUATION_CASE_TYPE_3),
]

IMAGE_TYPE_1 = _('Lokacija')
IMAGE_TYPE_2 = _('Priedas')
IMAGE_TYPE_3 = _('Planas')
IMAGE_TYPE_4 = _('Kita')

IMAGE_CHOICES = [
    (IMAGE_TYPE_1, IMAGE_TYPE_1),
    (IMAGE_TYPE_2, IMAGE_TYPE_2),
    (IMAGE_TYPE_3, IMAGE_TYPE_3),
    (IMAGE_TYPE_4, IMAGE_TYPE_4),
]





SIMILAR_OBJECT_TYPE_1 = _('Butai pardavimui')
SIMILAR_OBJECT_TYPE_2 = _('Namai pardavimui')
SIMILAR_OBJECT_TYPE_3 = _('Patalpos pardavimui')
SIMILAR_OBJECT_TYPE_4 = _('Sklypai')

SIMILAR_OBJECT_CHOICES = [
    ('butai', SIMILAR_OBJECT_TYPE_1),
    ('namai', SIMILAR_OBJECT_TYPE_2),
    ('patalpos', SIMILAR_OBJECT_TYPE_3),
    ('sklypai-pardavimui', SIMILAR_OBJECT_TYPE_4),
]





SIMILAR_OBJECT_MUNICIPALITY_CHOICES = [
    (VILNIUS_CITY, VILNIUS_CITY),
    (KAUNAS_CITY, KAUNAS_CITY),
    (KLAIPEDA_CITY, KLAIPEDA_CITY),
    (SIAULIAI_CITY, SIAULIAI_CITY),
    (PANEVEZYS_CITY, PANEVEZYS_CITY),
    (VILNIUS_DISTRICT, VILNIUS_DISTRICT),
    (KAUNAS_DISTRICT, KAUNAS_DISTRICT),
    (KLAIPEDA_DISTRICT, KLAIPEDA_DISTRICT),
    (SIAULIAI_DISTRICT, SIAULIAI_DISTRICT),
    (PANEVEZYS_DISTRICT, PANEVEZYS_DISTRICT),
    (ALYTUS_CITY, ALYTUS_CITY),
    (MARIJAMPOLE_CITY, MARIJAMPOLE_CITY),
    (UTENA_CITY, UTENA_CITY),
    (TAURAGE_CITY, TAURAGE_CITY),
    (TELŠIAI_CITY, TELŠIAI_CITY),
]


EQUIPMENT_TYPE_1 = _('Įrengtas')
EQUIPMENT_TYPE_2 = _('Dalinė apdaila')
EQUIPMENT_TYPE_3 = _('Neįrengtas')
EQUIPMENT_TYPE_4 = _('Nebaigtas statyti')
EQUIPMENT_TYPE_5 = _('Pamatai')
EQUIPMENT_TYPE_6 = _('Kita')

EQUIPMENT_CHOICES = [
    (EQUIPMENT_TYPE_1, EQUIPMENT_TYPE_1),
    (EQUIPMENT_TYPE_2, EQUIPMENT_TYPE_2),
    (EQUIPMENT_TYPE_3, EQUIPMENT_TYPE_3),
    (EQUIPMENT_TYPE_4, EQUIPMENT_TYPE_4),
    (EQUIPMENT_TYPE_5, EQUIPMENT_TYPE_5),
    (EQUIPMENT_TYPE_6, EQUIPMENT_TYPE_6),
]

SIMILAR_ACTION_TYPE_1 = _('Pardavimui')
SIMILAR_ACTION_TYPE_2 = _('Nuomai')

SIMILAR_ACTION_CHOICES = [
    (SIMILAR_ACTION_TYPE_1, SIMILAR_ACTION_TYPE_1),
    (SIMILAR_ACTION_TYPE_2, SIMILAR_ACTION_TYPE_2),
]

CATEGORY_CHOICES = {
    'school': _('Mokykla'),
    'hospital': _('Ligoninė'),
    'supermarket': _('Prekybos centras'),
    'pharmacy': _('Vaistinė'),
    'bakery': _('Kepykla'),
    'police': _('Policija'),
    'fire_station': _('Gaisrinė'),
    'post_office': _('Paštas'),
    'other': _('Kita')
}


REPORT_STATUS_CHOICES = [
    ('pending', _('Laukiama patvirtinimo')),
    ('approved', _('Patvirtinta')),
    ('rejected', _('Atmesta')),
]

NOTIFICATION_TYPES = [
    ('report_submission', _('Ataskaitos Pateikimas')),
    ('report_approval', _('Ataskaitos Patvirtinimas')),
    ('report_rejection', _('Ataskaitos Atmetimas')),
    ('order_assignment', _('Užsakymo pavedimas')),
    ('event', _('Kalendoriaus pranešimas')),
    ('system', _('Sistemos pranešimas')),
    ('event_transfer', _('Calendar Event Transfer')),
]

EVENT_TYPES = [
    ('meeting', _('Susitikimas')),
    ('deadline', _('Terminas')),
    ('site_visit', _('Objekto apžiūra')),
    ('other', _('Kita')),
]



RC_BUILDING_TYPE_CHOICES = [
    ('', _('Pasirinkite pastato tipą')),
    ('residential', _('Gyvenamasis')),
    ('commercial', _('Komercinis')),
    ('industrial', _('Pramoninis')),
    ('agricultural', _('Žemės ūkio')),
    ('public', _('Visuomeninės paskirties')),
    ('recreational', _('Rekreacinės paskirties')),
    ('other', _('Kita')),
]

RC_RIGHTS_TYPE_CHOICES = [
    ('', _('Pasirinkite teisių tipą')),
    ('ownership', _('Nuosavybės teisė')),
    ('lease', _('Nuoma')),
    ('usufruct', _('Uzufruktas')),
    ('easement', _('Servitutas')),
    ('mortgage', _('Hipoteka')),
    ('other', _('Kita')),
]

RC_LEGAL_STATUS_CHOICES = [
    ('', _('Pasirinkite juridinį statusą')),
    ('registered', _('Įregistruotas')),
    ('registration_in_progress', _('Registracija vykdoma')),
    ('unregistered', _('Neįregistruotas')),
    ('disputed', _('Ginčijamas')),
]
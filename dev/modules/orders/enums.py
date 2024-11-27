from django.utils.translation import gettext as _
from enum import Enum

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
    #POOL = _('Baseinas')
    #COMMERCIAL_TYPE = _('komercinis')
    #INDUSTRIAL_TYPE = _('Industrinis')
    #CULTURE_TYPE = _('Kultūros')
    #EDUCATION_TYPE = _('Mokslo')
    #RELAXATION_TYPE = _('Poilsio')

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

STATUS_CHOICES = (
    (_('Naujas'), _('Naujas')),
    (_('Patvirtintas'), _('Patvirtintas')),
    (_('Vykdomas'), _('Vykdomas')),
    (_('Įvykdytas'), _('Įvykdytas')),
    (_('Nepateiktas'), _('Nepateiktas')),
)

PRIORITY_CHOICES = (
    (_('žemas'), _('žemas')),
    (_('vidutinis'), _('vidutinis')),
    (_('aukštas'), _('aukštas'))
)

VILNIUS_CITY = _('Vilnius')
KAUNAS_CITY = _('Kaunas')
KLAIPEDA_CITY = _('Klaipėda')
SIAULIAI_CITY = _('Šiauliai')
PANEVEZYS_CITY = _('Panevėžys')
VILNIUS_DISTRICT = _('Vilniaus r.')
KAUNAS_DISTRICT = _('Kauno r.')
KLAIPEDA_DISTRICT = _('Klaipėdos r.')
SIAULIAI_DISTRICT = _('Šiaulių r.')
PANEVEZYS_DISTRICT = _('Panevėžio r.')


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
]

DECO_TYPE_1 = _('tinko paviršius tapetuotas')
DECO_TYPE_2 = _('tinko paviršius tapetuotas/dažytas')
DECO_TYPE_3 = _('tinko paviršius dažytas')
DECO_TYPE_4 = _('nėra')
DECO_CHOICES = [
    (DECO_TYPE_1, DECO_TYPE_1),
    (DECO_TYPE_2, DECO_TYPE_2),
    (DECO_TYPE_3, DECO_TYPE_3),
    (DECO_TYPE_4, DECO_TYPE_4),
]

FLOOR_CHOICE1 = _('betonas')
FLOOR_CHOICE2 = _('parketas')
FLOOR_CHOICE3 = _('laminatas')
FLOOR_CHOICE4 = _('minoliaumas')
FLOOR_CHOICES = [
    (FLOOR_CHOICE1, FLOOR_CHOICE1),
    (FLOOR_CHOICE2, FLOOR_CHOICE2),
    (FLOOR_CHOICE3, FLOOR_CHOICE3),
    (FLOOR_CHOICE4, FLOOR_CHOICE4),
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
FOUNDATION_TYPE_4 = _('Monolitiniai')
FOUNDATION_TYPE_5 = _('Plokštuminiai')
FOUNDATION_TYPE_6 = _('Iš blokų')

FOUNDATION_CHOICES = [
    (FOUNDATION_TYPE_1,  _('Gręžtiniai')),
    (FOUNDATION_TYPE_2, _('Monolitiniai')),
    (FOUNDATION_TYPE_3, _('Juostiniai')),
    (FOUNDATION_TYPE_4, _('Monolitiniai')),
    (FOUNDATION_TYPE_5, _('Plokštuminiai')),
    (FOUNDATION_TYPE_6, _('Iš blokų')),
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
PARTITION_TYPE_1 = _('Gipso kartono')
PARTITION_TYPE_2 = _('Mūrinė')
PARTITION_CHOICES = [
    (PARTITION_TYPE_1, _('Gipso kartono')),
    (PARTITION_TYPE_2, _('Mūrinė')),
]
OVERLAY_TYPE_1 = _('Gelžbetonio plokštės')
OVERLAY_CHOICES = [
    (OVERLAY_TYPE_1, _('Gelžbetonio plokštės')),
]
ROOF_TYPE_1 = _('Šlaitinis')
ROOF_TYPE_2 = _('Plokščias')
ROOF_CHOICES = [
    (ROOF_TYPE_1, _('Šlaitinis')),
    # šiferis,skarda,bituminė danga, betoninės čerpės, keramikinės čerpės
    (ROOF_TYPE_2, _('Plokščias')),
    # plieninė danga, prilydoma danga, bituminės čerpės, skalūnas,fibrocementinės plokštelės
]

SHED_TYPE_1 = _('Karkasinis')
SHED_TYPE_2 = _('Mūrinis')
SHED_CHOICES = [
    (SHED_TYPE_1, _('Karkasinis')),
    (SHED_TYPE_2, _('Mūrinis')),
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


ELECTRICITY_TYPE_1 = _('nėra')
ELECTRICITY_TYPE_2 = _('ESO')
ELECTRICITY_GAS_CHOICES = [
    (ELECTRICITY_TYPE_1, _('nėra')),
    (ELECTRICITY_TYPE_2, _('ESO')),
]

HEATING_TYPE_1 = _('Nėra')
HEATING_TYPE_2 = _('Centralizuotas')
HEATING_TYPE_3 = _('Vietinis')
HEATING_TYPE_4 = _('Kita')
HEATING_CHOICES = [
    (HEATING_TYPE_1, _('Nėra')),
    (HEATING_TYPE_2, _('Centralizuotas')),
    (HEATING_TYPE_3, _('Vietinis')),
    (HEATING_TYPE_4, _('Kita')),
]

WATER_SUPPLY_CHOICES = [
    (EXIST_TYPE_1, EXIST_TYPE_1),
    (EXIST_TYPE_2, EXIST_TYPE_2),
]

WASTEWATER_CHOICE2 = _('Komunalinis nuotekų šalinimas')
WASTEWATER_CHOICES = [
    (EXIST_TYPE_2, EXIST_TYPE_2),
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
COOLING_CHOICES = [
    (COOLING_TYPE_1, _('Oras-oras')),
    (EXIST_TYPE_2, EXIST_TYPE_2),
]

WINDOW_TYPE_1 = _('plastikiniai')
WINDOW_TYPE_2 = _('aliuminio')
WINDOW_TYPE_3 = _('mediniai')
WINDOW_TYPE_4 = _('aliuminio-medienios')
WINDOW_CHOICES = [
    (WINDOW_TYPE_1, _('plastikiniai')),
    (WINDOW_TYPE_2, _('aliuminio')),
    (WINDOW_TYPE_3, _('mediniai')),
    (WINDOW_TYPE_4, _('aliuminio-medienios')),
]

INNER_DOOR_TYPE_1 = _('laminuotos')
INNER_DOOR_TYPE_2 = _('medinės')
INNER_DOOR_TYPE_3 = _('faneruotos')
INNER_DOOR_TYPE_4 = _('plastikinės')
INNER_DOOR_CHOICES = [
    (INNER_DOOR_TYPE_1, _('laminuotos')),
    (INNER_DOOR_TYPE_2, _('medinės')),
    (INNER_DOOR_TYPE_3, _('faneruotos')),
    (INNER_DOOR_TYPE_4, _('plastikinės')),
]
OUTER_DOOR_TYPE_1 = _('medinės')
OUTER_DOOR_TYPE_2 = _('šarvo')
OUTER_DOOR_CHOICES = [
    (OUTER_DOOR_TYPE_1, _('medinės')),
    (OUTER_DOOR_TYPE_2, _('šarvo')),
]


PURPOSE_TYPE_1 = _('Gyvenamoji')
PURPOSE_TYPE_2 = _('Žemės ūkio')
PURPOSE_TYPE_3 = _('Komercinė')
PURPOSE_TYPE_4 = _('Kita')
PURPOSE_CHOICES = [
    (PURPOSE_TYPE_1,PURPOSE_TYPE_1),
    (PURPOSE_TYPE_2,PURPOSE_TYPE_2),
    (PURPOSE_TYPE_3,PURPOSE_TYPE_3),
    (PURPOSE_TYPE_4,PURPOSE_TYPE_4),
]
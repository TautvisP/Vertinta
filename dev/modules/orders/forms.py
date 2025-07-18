from django import forms
from modules.orders.models import Order, Event
from django.utils.translation import gettext as _
from .enums import FOUNDATION_CHOICES, WALLS_CHOICES, PARTITION_CHOICES, OVERLAY_CHOICES, EVENT_TYPES, PRIORITY_CHOICES, ROOF_CHOICES, WINDOW_CHOICES, INNER_DOOR_CHOICES, OUTER_DOOR_CHOICES, STATUS_CHOICES, DECO_CHOICES, FLOOR_CHOICES, ELECTRICITY_GAS_CHOICES, HEATING_CHOICES, WATER_SUPPLY_CHOICES, WASTEWATER_CHOICES, SECURITY_CHOICES, BOOL_CHOICES, OUTDOOR_DECO_CHOICES, ENERGY__EFFICIENCY_CHOICES, COOLING_CHOICES, LAND_PURPOSE_CHOICES, SHED_CHOICES, GAZEBO_CHOICES, EXIST_CHOICES, MUNICIPALITY_CHOICES

default_errors = {
    'invalid': _("Įveskite skaičių."),
    'required': _("Šis laukas turi būti užpildytas."),
    'max_length': _('Užtikrintike, kad ši reikšmė turi daugiausiai %(limit_value)d simbolių (dabar turi %(show_value)d).'),
    'min_length': _('Užtikrintike, kad ši reikšmė turi ne mažiau nei %(limit_value)d simbolių (dabar turi %(show_value)d).'),
    'min_value': _('Užtikrinkite, kad ši reikšmė yra didesnė arba lygi %(limit_value)s.'),
    'max_value': _('Užtikrinkite, kad ši reikšmė yra mažesnė arba lygi %(limit_value)s.')
}


class HouseRequestConditionForm(forms.Form):
    foundation = forms.ChoiceField(label=_('Pamatai'), choices=FOUNDATION_CHOICES,
                                   widget=forms.Select(attrs={'class': 'form-control'}))
    
    walls = forms.ChoiceField(label=_('Sienos'), choices=WALLS_CHOICES,
                              widget=forms.Select(attrs={'class': 'form-control'}))
    
    partition = forms.ChoiceField(label=_('Pertvaros'), choices=PARTITION_CHOICES,
                                  widget=forms.Select(attrs={'class': 'form-control'}))
    
    overlay = forms.ChoiceField(label=_('Perdanga'), choices=OVERLAY_CHOICES,
                                widget=forms.Select(attrs={'class': 'form-control'}))
    
    roof = forms.ChoiceField(label=_('Stogas'), choices=ROOF_CHOICES,
                             widget=forms.Select(attrs={'class': 'form-control'}))


class ObjectLocationForm(forms.Form):
    municipality = forms.ChoiceField(
        label=_('Savivaldybė'), choices=MUNICIPALITY_CHOICES, widget=forms.Select( attrs={'class': 'form-control'}))
    
    street = forms.CharField(
        label=_('Gatvė'), max_length=100, error_messages=default_errors)
    
    house_no = forms.IntegerField(
        label=_('Namo nr.'),  min_value=1, error_messages=default_errors)
    
    latitude = forms.DecimalField(
        label=_('Platuma'), max_digits=9, decimal_places=6, widget=forms.NumberInput(attrs={'class': 'form-control'}), error_messages=default_errors)
    
    longitude = forms.DecimalField(
        label=_('Ilguma'), max_digits=9, decimal_places=6, widget=forms.NumberInput(attrs={'class': 'form-control'}), error_messages=default_errors)


    def get_fields(self, *args, **kwargs):
        super(ObjectLocationForm, self).__init__(*args, **kwargs)
        field_dict = self.fields
        field_list = []

        for key in field_dict.keys():
            field_list.append(key)

        return field_list




class DecorationForm(forms.Form):
    outside_deco = forms.ChoiceField(
        label=_('Išorės apdaila'), choices=OUTDOOR_DECO_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    ceiling_deco = forms.ChoiceField(
        label=_('Lubos'), choices=DECO_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    interior_floors = forms.ChoiceField(
        label=_('Grindys'), choices=FLOOR_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    interior_deco = forms.ChoiceField(
        label=_('Interjero apdaila'), choices=DECO_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    def get_fields(self, *args, **kwargs):
        super(DecorationForm, self).__init__(*args, **kwargs)
        field_dict = self.fields
        field_list = []

        for key in field_dict.keys():
            field_list.append(key)

        return field_list




class UtilityForm(forms.Form):
    electricity = forms.ChoiceField(
        label=_('Elektra'), choices=ELECTRICITY_GAS_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    water = forms.ChoiceField(
        label=_('Vandentiekis'), choices=WATER_SUPPLY_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    gas = forms.ChoiceField(
        label=_('Dujos'), choices=ELECTRICITY_GAS_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    wastewater = forms.ChoiceField(
        label=_('Nuotekų valymas'), choices=WASTEWATER_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    heating = forms.ChoiceField(
        label=_('Šildymas'), choices=HEATING_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    security = forms.ChoiceField(
        label=_('Signalizacija'), choices=SECURITY_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    energy_efficiency = forms.ChoiceField(
        label=_('Energinis naudingumas'), choices=ENERGY__EFFICIENCY_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    air_conditioning = forms.ChoiceField(
        label=_('Vėdinimas/kondicionavimas'), choices=COOLING_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    parking_spaces = forms.IntegerField(
        label=_('Vieta automobiliui'),  min_value=0, error_messages=default_errors)

    def get_fields(self, *args, **kwargs):
        super(UtilityForm, self).__init__(*args, **kwargs)
        field_dict = self.fields
        field_list = []

        for key in field_dict.keys():
            field_list.append(key)
            
        return field_list




class CommonInformationForm(forms.Form):
    foundation = forms.ChoiceField(
        label=_('Pamatai'), choices=FOUNDATION_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    walls = forms.ChoiceField(
        label=_('Sienos'), choices=WALLS_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    inside_walls = forms.ChoiceField(
        label=_('Pertvaros'), choices=PARTITION_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    subfloor = forms.ChoiceField(
        label=_('Pogrindis'), choices=OVERLAY_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    basement = forms.ChoiceField(
        label=_('Rusys'), choices=EXIST_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    balcony = forms.ChoiceField(
        label=_('Balkonas'), choices=EXIST_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    roof = forms.ChoiceField(
        label=_('Stogas'), choices=ROOF_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    windows = forms.ChoiceField(
        label=_('Langai'), choices=WINDOW_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    inside_doors = forms.ChoiceField(
        label=_('Vidaus durys'), choices=INNER_DOOR_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    outside_doors = forms.ChoiceField(
        label=_('Išorės durys'), choices=OUTER_DOOR_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    build_years = forms.DateField(
        label=_('Pastatymo metai'), widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    
    renovation_years = forms.DateField(
        label=_('Renovacijos metai'), widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))

    room_count = forms.IntegerField(
        label=_('Kambarių skaičius'), min_value=1, error_messages=default_errors)
    
    living_size = forms.IntegerField(
        label=_('Kvadratūra, m2'), min_value=1, error_messages=default_errors)
    
    def clean(self):
        cleaned_data = super().clean()
        build_years = cleaned_data.get('build_years')
        renovation_years = cleaned_data.get('renovation_years')

        if build_years and renovation_years:
            if renovation_years < build_years:
                raise forms.ValidationError(
                    _('Renovacijos metai negali būti mažesni nei pastatymo metai.')
                )

        return cleaned_data

    def get_fields(self, *args, **kwargs):
        super(CommonInformationForm, self).__init__(*args, **kwargs)
        field_dict = self.fields
        field_list = []

        for key in field_dict.keys():
            field_list.append(key)

        return field_list




class GarageForm(forms.Form):
    garage_attached = forms.ChoiceField(
        label=_('Sujungtas su namu'), choices=BOOL_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    garage_size = forms.IntegerField(
        label=_('Kvadratūra, m2'), min_value=1, error_messages=default_errors)
    
    garage_cars_count = forms.IntegerField(
        label=_('Telpa automobilių'), min_value=0, error_messages=default_errors)

    def get_fields(self, *args, **kwargs):
        super(GarageForm, self).__init__(*args, **kwargs)
        field_dict = self.fields
        field_list = []

        for key in field_dict.keys():
            field_list.append(key)

        return field_list




class ShedForm(forms.Form):
    shed_electricity = forms.ChoiceField(
        label=_('Elektros instaliacija'), choices=EXIST_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    shed_size = forms.IntegerField(
        label=_('Kvadratūra, m2'), min_value=1, error_messages=default_errors)
    
    shed_type = forms.ChoiceField(
        label=_('Tipas'), choices=SHED_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    def get_fields(self, *args, **kwargs):
        super(ShedForm, self).__init__(*args, **kwargs)
        field_dict = self.fields
        field_list = []

        for key in field_dict.keys():
            field_list.append(key)

        return field_list




class GazeboForm(forms.Form):
    gazebo_electricity = forms.ChoiceField(
        label=_('Elektros instaliacija'), choices=EXIST_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    gazebo_size = forms.IntegerField(
        label=_('Kvadratūra, m2'), min_value=1, error_messages=default_errors)
    
    gazebo_type = forms.ChoiceField(
        label=_('Tipas'), choices=GAZEBO_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    def GazeboForm(self, *args, **kwargs):
        super(ShedForm, self).__init__(*args, **kwargs)
        field_dict = self.fields
        field_list = []

        for key in field_dict.keys():
            field_list.append(key)

        return field_list
    



class LandForm(forms.Form):
    land_purpose = forms.ChoiceField(
        label=_('Sklypo paskirtis'), choices=LAND_PURPOSE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    land_size = forms.IntegerField(
        label=_('Sklypo plotas, a'), min_value=1, error_messages=default_errors)

    def get_fields(self, *args, **kwargs):
        super(LandForm, self).__init__(*args, **kwargs)
        field_dict = self.fields
        field_list = []

        for key in field_dict.keys():
            field_list.append(key)

        return field_list




class HouseForm(forms.Form):
    land_purpose = forms.ChoiceField(
        label=_('Sklypo paskirtis'), choices=LAND_PURPOSE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    land_size = forms.IntegerField(
        label=_('Sklypo plotas, a'), min_value=1, error_messages=default_errors)
    
    floor_count = forms.IntegerField(
        label=_('Aukštų skaičius'), min_value=1, error_messages=default_errors)

    def get_fields(self, *args, **kwargs):
        super(HouseForm, self).__init__(*args, **kwargs)
        field_dict = self.fields
        field_list = []

        for key in field_dict.keys():
            field_list.append(key)

        return field_list




class CottageForm(forms.Form):
    floor_count = forms.IntegerField(
        label=_('Aukštų skaičius'), min_value=1, error_messages=default_errors)

    def get_fields(self, *args, **kwargs):
        super(CottageForm, self).__init__(*args, **kwargs)
        field_dict = self.fields
        field_list = []

        for key in field_dict.keys():
            field_list.append(key)

        return field_list




class ApartamentForm(forms.Form):
    building_floor_count = forms.IntegerField(
        label=_('Pastato aukštų skaičius'), min_value=1, error_messages=default_errors)
    
    apartament_floor = forms.IntegerField(
        label=_('Buto aukštas'), min_value=1, error_messages=default_errors)

    def get_fields(self, *args, **kwargs):
        super(ApartamentForm, self).__init__(*args, **kwargs)
        field_dict = self.fields
        field_list = []

        for key in field_dict.keys():
            field_list.append(key)
            
        return field_list




class OrderStatusForm(forms.ModelForm):
    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    priority = forms.ChoiceField(choices=PRIORITY_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Order
        fields = ['status', 'priority']

    
class EventForm(forms.ModelForm):
    """Form for creating and editing calendar events."""
    
    start_time = forms.DateTimeField(
        label=_('Pradžios laikas'),
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local', 'class': 'form-control'},
            format='%Y-%m-%dT%H:%M'
        ),
    )
    
    title = forms.CharField(
        label=_('Pavadinimas'),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    description = forms.CharField(
        label=_('Aprašymas'),
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    
    event_type = forms.ChoiceField(
        label=_('Tipas'),
        choices=EVENT_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    location = forms.CharField(
        label=_('Vieta'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Event
        fields = ['title', 'description', 'event_type', 'start_time', 'location']
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        
        return cleaned_data
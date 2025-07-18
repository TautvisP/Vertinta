import datetime
from decimal import Decimal
from django import forms
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from core.uauth.models import User, UserMeta
from ..orders.enums import (HOUSE_TYPE_CHOICES, FLOOR_COUNT_CHOICES, RC_RIGHTS_TYPE_CHOICES, STATUS_CHOICES, RC_LEGAL_STATUS_CHOICES, RC_BUILDING_TYPE_CHOICES, HEATING_CHOICES,COMERCIAL_CHOICES, BUILDING_CHOICES, EQUIPMENT_CHOICES, SIMILAR_OBJECT_CHOICES, SIMILAR_ACTION_CHOICES, MUNICIPALITY_CHOICES, LAND_PURPOSE_CHOICES, EVALUATION_PURPOSE_CHOICES, EVALUATION_CASE_CHOICES, IMAGE_CHOICES, CATEGORY_CHOICES, OBJECT_TYPE_CHOICES )
from ..orders.models import ObjectImage, ImageAnnotation, Report, ObjectMeta
from django.utils.translation import gettext as _

class EvaluatorEditForm(UserChangeForm):
    first_name = forms.CharField(
        label=_('Vardas'), 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label=_('Pavardė'), 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    qualification_certificate_number = forms.CharField(
        label=_('Kvalifikacijos pažymėjimo numeris'), 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    date_of_issue_of_certificate = forms.DateField(
        label=_('Pažymėjimo išdavimo data'), 
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    email = forms.EmailField(
        label=_('El. paštas'), 
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone_num = forms.CharField(
        label=_('Telefono numeris'), 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['qualification_certificate_number'].initial = UserMeta.get_meta(self.instance, 'qualification_certificate_number')
        self.fields['date_of_issue_of_certificate'].initial = UserMeta.get_meta(self.instance, 'date_of_issue_of_certificate')
        self.fields['phone_num'].initial = UserMeta.get_meta(self.instance, 'phone_num')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
            self.save_meta(user)
        return user

    def save_meta(self, user):
        meta_fields = ['qualification_certificate_number', 'date_of_issue_of_certificate', 'phone_num']
        
        for field in meta_fields:
            value = self.cleaned_data.get(field)
            
            if value:
                UserMeta.objects.update_or_create(
                    user=user, meta_key=field, defaults={'meta_value': value}
                )

class EvaluatorPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label=_('Senas slaptažodis'), 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label=_('Naujas slaptažodis'), 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label=_('Pakartokite naują slaptažodį'), 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


class EvaluationForm(forms.Form):
    evaluation_purpose = forms.ChoiceField(
        label=_('Vertinimo tikslas'), choices=EVALUATION_PURPOSE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    evaluation_case = forms.ChoiceField(
        label=_('Vertinimo atvejis'), choices=EVALUATION_CASE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    object_condition = forms.CharField(
        label=_('Turto būklė'), widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    object_completness = forms.CharField(
        label=_('Turto baigtumas, %'), widget=forms.TextInput(attrs={'class': 'form-control'}))
    

class ObjectImageForm(forms.ModelForm):
    class Meta:
        model = ObjectImage
        fields = ['image', 'comment', 'category']

    image = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'id': 'file-input'
        })
    )

    comment = forms.CharField(
        label=_('Komentaras'), widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    category = forms.ChoiceField(
        label=_('Kategorija'), choices=IMAGE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    

class ImageAnnotationForm(forms.ModelForm):
    x_coordinate = forms.FloatField(
        widget=forms.HiddenInput())
    
    y_coordinate = forms.FloatField(
        widget=forms.HiddenInput())
    
    annotation_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': _('Anotacijos tekstas')
        }), required=False)
        
    annotation_image = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'id': 'annotation-image-input'
        }), required=False)
    
    class Meta:
        model = ImageAnnotation
        fields = ['x_coordinate', 'y_coordinate', 'annotation_text', 'annotation_image']


# This is used for collecting search criteria for butas object in aruodas website
class ButasSearchForm(forms.Form):
    municipality = forms.ChoiceField(
        choices=MUNICIPALITY_CHOICES, label=_('Savivaldybė'))
    
    area_from = forms.IntegerField(
        label=_('Plotas, nuo (m2)'), min_value=0)
    
    area_to = forms.IntegerField(
        label=_('Plotas, iki (m2)'), min_value=0)
    
    equipment = forms.ChoiceField(
        choices=EQUIPMENT_CHOICES, label=_('Įrengimas'))
    
    room_count_from = forms.IntegerField(
        label=_('Kambarių skaičius nuo'), min_value=1)
    
    room_count_to = forms.IntegerField(
        label=_('Kambarių skaičius iki'), min_value=1)
    
    price_from = forms.IntegerField(
        label=_('Kaina nuo'), min_value=0)
    
    price_to = forms.IntegerField(
        label=_('Kaina iki'), min_value=0)



# This is used for collecting search criteria for namas object in aruodas website
class NamasSearchForm(forms.Form):
    house_type = forms.ChoiceField(
        choices=HOUSE_TYPE_CHOICES, label=_('Namo tipas'))
    
    municipality = forms.ChoiceField(
        choices=MUNICIPALITY_CHOICES, label=_('Savivaldybė'))
    
    area_from = forms.IntegerField(
        label=_('Plotas, nuo (m2)'), min_value=0)
    
    area_to = forms.IntegerField(
        label=_('Plotas, iki (m2)'), min_value=0)
    
    equipment = forms.ChoiceField(
        choices=EQUIPMENT_CHOICES, label=_('Įrengimas'))
    
    price_from = forms.IntegerField(
        label=_('Kaina nuo'), min_value=0)
    
    price_to = forms.IntegerField(
        label=_('Kaina iki'), min_value=0)
    
    land_area_from = forms.IntegerField(
        label=_('Sklypo plotas nuo (a)'), min_value=0)
    
    land_area_to = forms.IntegerField(
        label=_('Sklypo plotas iki (a)'), min_value=0)
    
    floors = forms.ChoiceField(
        choices=FLOOR_COUNT_CHOICES, label=_('Aukštų skaičius'))
    
    heating = forms.ChoiceField(
        choices=HEATING_CHOICES, label=_('Šildymas'))
    
    building_type = forms.ChoiceField(
        choices=BUILDING_CHOICES, label=_('Pastato tipas'))



# This is used for collecting search criteria for patalpos object in aruodas website
class PatalposSearchForm(forms.Form):
    municipality = forms.ChoiceField(
        choices=MUNICIPALITY_CHOICES, label=_('Savivaldybė'))
    
    area_from = forms.IntegerField(
        label=_('Plotas, nuo (m2)'), min_value=0)
    
    area_to = forms.IntegerField(
        label=_('Plotas, iki (m2)'), min_value=0)
    
    equipment = forms.ChoiceField(
        choices=EQUIPMENT_CHOICES, label=_('Įrengimas'))
    
    price_from = forms.IntegerField(
        label=_('Kaina nuo'), min_value=0)
    
    price_to = forms.IntegerField(
        label=_('Kaina iki'), min_value=0)
    
    purpose = forms.ChoiceField(
        choices=COMERCIAL_CHOICES, label=_('Paskirtis'))



# This is used for collecting search criteria for sklypas object in aruodas website
class SklypaiSearchForm(forms.Form):
    action = forms.ChoiceField(
        choices=SIMILAR_ACTION_CHOICES, label=_('Veiksmas'))
    
    land_area_from = forms.IntegerField(
        label=_('Sklypo plotas nuo (a)'), min_value=0)
    
    land_area_to = forms.IntegerField(
        label=_('Sklypo plotas iki (a)'), min_value=0)
    
    municipality = forms.ChoiceField(
        choices=MUNICIPALITY_CHOICES, label=_('Savivaldybė'))
    
    equipment = forms.ChoiceField(
        choices=EQUIPMENT_CHOICES, label=_('Įrengimas'))
    
    price_from = forms.IntegerField(
        label=_('Kaina nuo'), min_value=0)
    
    price_to = forms.IntegerField(
        label=_('Kaina iki'), min_value=0)
    
    purpose = forms.ChoiceField(
        choices=LAND_PURPOSE_CHOICES, label=_('Paskirtis'))


class SimilarObjectTypeSelectionForm(forms.Form):
    object_type = forms.ChoiceField(
        choices=SIMILAR_OBJECT_CHOICES, label=_('Panašaus objekto tipas'))

# similar object type = butai pardavimui
# search criteria: plotas nuo, iki; savivaldybe; kambariu skaicius nuo, iki; irengimas;  kaina nuo, iki; 

# similar object type = namai pardavimui
# search criteria: namo tipas (enum: namas, namo dalis, sodo namas, sublokuotas namas, sodyba, kita); plotas nuo, iki; savivaldybe; kambariu skaicius nuo, iki; irengimas;  kaina nuo, iki; sklypo plotas nuo, iki; aukstu skaicius(enum: 1, 2, daugiau nei 2); šildymas (enum: Centrinis, centrinis kolektorinis, dujinis, elektra, aeroterminis, geoterminis, skystu kuru, kietu kuru, saules energija, kita); pastato tipas(enum: murinis, blokinis, monolitinis, medinis, karkasinis, rastinis, skydinis, kita)

# similar object type = patalpos pardavimui
# search criteria: plotas nuo, iki; savivaldybe; irengimas;  kaina nuo, iki; paskirtis (enum: administracine, prekybos, viesbuciu, paslaugu, sandeliavimo, gamybos ir pramones, maitinimo, medicinos kita)

# similar object type = sklypai
# search criteria: veiksmas(enum: pardavimui, nuomai) sklypo plotas nuo, iki; savivaldybe; irengimas;  kaina nuo, iki; paskirtis (enum: namu valda, daugiabuciu statyba, zemes ukio, sklypas soduose, misku ukio, pramones, sandeliavimo, komenrcine, rekreacine, kita)

# similar object type = sodybos
# search criteria: veiksmas(enum: pardavimui, nuomai) sklypo plotas nuo, iki; savivaldybe; irengimas;  kaina nuo, iki; paskirtis (enum: namu valda, daugiabuciu statyba, zemes ukio, sklypas soduose, misku ukio, pramones, sandeliavimo, komenrcine, rekreacine, kita)



class SimilarObjectForm(forms.Form):
    price = forms.FloatField(
        label=_('Objekto kaina'), min_value=0)
    
    link = forms.CharField(
        label=_('Skelbimo nuoroda'), 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    description = forms.CharField(
        label=_('Panašaus objekto aprašymas'), 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )



class TextFileUploadForm(forms.Form):
    file = forms.FileField(
        label=_('Tekstinis failas'), widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    
    comment = forms.CharField(
        label=_('Komentaras'), widget=forms.TextInput(attrs={'class': 'form-control'}))
    



class NearbyOrganizationForm(forms.Form):
    name = forms.CharField(
        label=_('Pavadinimas'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Pavadinimas')
        })
    )
    
    category = forms.ChoiceField(
        label=_('Kategorija'),
        choices=CATEGORY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': _('Kategorija')
        })
    )
    
    address = forms.CharField(
        label=_('Adresas'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Adresas')
        })
    )
    
    distance = forms.DecimalField(
        label=_('Atstumas iki vertinamo objekto'),
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('Atstumas, m')
        })
    )
    
    latitude = forms.DecimalField(
        label=_('Platuma'),
        max_digits=9,
        decimal_places=6,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('54.906638')
        })
    )
    
    longitude = forms.DecimalField(
        label=_('Ilguma'),
        max_digits=9,
        decimal_places=6,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('25.319142')
        })
    )





class FinalReportForm(forms.ModelForm):
    visit_date = forms.DateField(
        label=_('Turto apžiūros data'),
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    report_date = forms.DateField(
        label=_('Ataskaitos data'),
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    description = forms.CharField(
        label=_('Aprašymas'),
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': _('Įveskite aprašymą')
        })
    )
    
    class Meta:
        model = Report
        fields = ['visit_date', 'report_date', 'description']
        widgets = {
            'visit_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'report_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Įveskite aprašymą')}),
        }






class FinalReportEngineeringForm(forms.ModelForm):
    engineering = forms.CharField(
        label=_('Inžinerinė įranga'),
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': _('Įveskite aprašymą apie inžinerinę įrangą')
        })
    )

    addictions = forms.CharField(
        label=_('Priklausiniai'),
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': _('Priklausiniai')
        })
    )

    floor_plan = forms.CharField(
        label=_('Erdvinis išplanavimas'),
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': _('Erdvinis išplanavimas')
        })
    )

    district = forms.CharField(
        label=_('Rajono aprašymas'),
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': _('Rajono aprašymas')
        })
    )

    conclusion = forms.CharField(
        label=_('Išvada'),
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': _('Išvada')
        })
    )

    valuation_methodology = forms.CharField(
        label=_('Vertinimo metodika'),
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': _('Pritaikyta vertinimo metodika')
        })
    )

    class Meta:
        model = Report
        fields = ['engineering', 'addictions', 'floor_plan', 'district', 'conclusion', 'valuation_methodology']
        widgets = {
            'engineering': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Įveskite aprašymą apie inžinerinę įrangą')}),
            'addictions': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Priklausiniai')}),
            'floor_plan': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Erdvinis išplanavimas')}),
            'district': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Rajono aprašymas')}),
            'conclusion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Išvada')}),
            'valuation_methodology': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Pritaikyta vertinimo metodika')}),
        }



class RCForm(forms.ModelForm):
    property_code = forms.CharField(
        label=_('Unikalus numeris'),
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Įveskite unikalų objekto numerį')
        })
    )
    
    cadastral_code = forms.CharField(
        label=_('Kadastro numeris'),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Įveskite kadastro numerį')
        })
    )
    
    building_type = forms.ChoiceField(
        label=_('Pastato tipas'),
        choices=RC_BUILDING_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    property_value = forms.DecimalField(
        label=_('Vidutinė rinkos vertė (EUR)'),
        max_digits=12,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('Įveskite vertę')
        })
    )
    
    value_determination_date = forms.DateField(
        label=_('Vertės nustatymo data'),
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    cadastral_value = forms.DecimalField(
        label=_('Kadastrinė vertė (EUR)'),
        max_digits=12,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('Įveskite kadastrinę vertę')
        })
    )
    
    total_area = forms.DecimalField(
        label=_('Bendras plotas (m²)'),
        max_digits=8,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('Įveskite bendrą plotą')
        })
    )
    
    useful_area = forms.DecimalField(
        label=_('Naudingas plotas (m²)'),
        max_digits=8,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('Įveskite naudingą plotą')
        })
    )
    
    legal_registration_date = forms.DateField(
        label=_('Teisinės registracijos data'),
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    rights_type = forms.ChoiceField(
        label=_('Teisių tipas'),
        choices=RC_RIGHTS_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    legal_status = forms.ChoiceField(
        label=_('Juridinis statusas'),
        choices=RC_LEGAL_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    physical_wear_percentage = forms.DecimalField(
        label=_('Fizinis nusidėvėjimas (%)'),
        max_digits=5,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('Įveskite fizinį nusidėvėjimą')
        })
    )
    
    notes = forms.CharField(
        label=_('Papildoma informacija'),
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': _('Papildoma informacija iš Registrų Centro'),
            'rows': 4
        })
    )
    
    class Meta:
        model = ObjectMeta
        fields = [
            'property_code', 'cadastral_code', 'building_type', 
            'property_value', 'value_determination_date', 'cadastral_value',
            'total_area', 'useful_area', 'legal_registration_date', 'rights_type',
            'legal_status', 'physical_wear_percentage', 'notes'
        ]
    
    def __init__(self, *args, **kwargs):
        obj = kwargs.pop('obj', None)
        super().__init__(*args, **kwargs)
        
        #Populate the data if the object already exists
        if obj:
            meta_data = ObjectMeta.objects.filter(ev_object=obj)
            for meta in meta_data:
                key = meta.meta_key
                if key.startswith('rc_'):
                    key = key[3:]
                
                if key in self.fields:
                    self.fields[key].initial = meta.meta_value
    

    def save(self, obj=None, commit=True):
        """
        Custom save method to save RC data as ObjectMeta entries
        """
        if not obj:
            raise ValueError("Object instance must be provided to save RC data")
        
        instance = super().save(commit=False)
        
        # Save each field as a separate ObjectMeta record with rc_ prefix
        if commit:
            for field_name, value in self.cleaned_data.items():
                if value is not None:
                    if isinstance(value, (datetime.date, datetime.datetime)):
                        value = value.isoformat()
                    elif isinstance(value, (Decimal, int, float)):
                        value = str(value)
                    
                    meta_key = f"rc_{field_name}"
                    
                    ObjectMeta.objects.update_or_create(
                        ev_object=obj,
                        meta_key=meta_key,
                        defaults={'meta_value': value}
                    )
        
        return instance
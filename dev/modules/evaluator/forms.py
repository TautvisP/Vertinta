from django import forms
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from core.uauth.models import User, UserMeta
from ..orders.enums import (HOUSE_TYPE_CHOICES, FLOOR_COUNT_CHOICES, HEATING_CHOICES,COMERCIAL_CHOICES, BUILDING_CHOICES, EQUIPMENT_CHOICES, SIMILAR_OBJECT_CHOICES, SIMILAR_ACTION_CHOICES, MUNICIPALITY_CHOICES, LAND_PURPOSE_CHOICES, EVALUATION_PURPOSE_CHOICES, EVALUATION_CASE_CHOICES, IMAGE_CHOICES )
from ..orders.models import ObjectImage, ImageAnnotation
from django.utils.translation import gettext as _

class EvaluatorEditForm(UserChangeForm):
    name = forms.CharField(
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
        fields = ('name', 'last_name', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['name']
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
        label=_('Nuotrauka'), widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

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
        label=_('Anotacijos tekstas'), widget=forms.Textarea(attrs={'class': 'form-control'}), required=False)
    
    annotation_image = forms.ImageField(
        label=_('Anotacijos nuotrauka'), widget=forms.ClearableFileInput(attrs={'class': 'form-control'}), required=False)
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
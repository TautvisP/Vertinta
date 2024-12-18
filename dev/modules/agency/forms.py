from django import forms
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm, UserCreationForm
from core.uauth.models import User, UserMeta
from modules.orders.enums import MUNICIPALITY_CHOICES
from django.utils.translation import gettext as _
class AgencyEditForm(UserChangeForm):
    agency_name = forms.CharField(
        label=_('Agentūros pavadinimas'), 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    main_city = forms.ChoiceField(
        label=_('Pagrindinis miestas'), 
        choices=MUNICIPALITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label=_('El. paštas'), 
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone_num = forms.CharField(
        label=_('Telefono numeris'), 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    evaluation_starting_price = forms.DecimalField(
        label=_('Vertinimo pradinė kaina'), 
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('email',)

    def save(self, commit=True):
        user = super().save(commit=False)

        if commit:
            user.save()
            self.save_meta(user)
            
        return user

    def save_meta(self, user):
        meta_fields = ['agency_name', 'main_city', 'phone_num', 'evaluation_starting_price']

        for field in meta_fields:
            value = self.cleaned_data.get(field)

            if value:
                UserMeta.objects.update_or_create(
                    user=user, meta_key=field, defaults={'meta_value': value}
                )


class AgencyPasswordChangeForm(PasswordChangeForm):
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


class EvaluatorCreationForm(UserCreationForm):
    first_name = forms.CharField(
        label=_('Vardas'), 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label=_('Pavardė'), 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label=_('El. paštas'), 
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label=_('Slaptažodis'), 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label=_('Pakartokite slaptažodį'), 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = True

        if commit:
            user.save()

        return user
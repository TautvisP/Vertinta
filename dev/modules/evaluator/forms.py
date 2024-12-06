from django import forms
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from core.uauth.models import User, UserMeta
from ..orders.enums import *
from ..orders.models import *


class EvaluatorEditForm(UserChangeForm):
    name = forms.CharField(
        label='Vardas', 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label='Pavardė', 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    qualification_certificate_number = forms.CharField(
        label='Kvalifikacijos pažymėjimo numeris', 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    date_of_issue_of_certificate = forms.DateField(
        label='Pažymėjimo išdavimo data', 
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    email = forms.EmailField(
        label='El. paštas', 
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone_num = forms.CharField(
        label='Telefono numeris', 
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
        label='Senas slaptažodis', 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label='Naujas slaptažodis', 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label='Pakartokite naują slaptažodį', 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


class EvaluationForm(forms.Form):
    evaluation_purpose = forms.ChoiceField(
        label='Vertinimo tikslas', choices=EVALUATION_PURPOSE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    evaluation_case = forms.ChoiceField(
        label='Vertinimo atvejis', choices=EVALUATION_CASE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    object_condition = forms.CharField(
        label='Turto būklė', widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    object_completness = forms.CharField(
        label='Turto baigtumas, %', widget=forms.TextInput(attrs={'class': 'form-control'}))
    

class ObjectImageForm(forms.ModelForm):
    class Meta:
        model = ObjectImage
        fields = ['image', 'comment', 'category']

    image = forms.ImageField(
        label='Nuotrauka', widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

    comment = forms.CharField(
        label='Komentaras', widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    category = forms.ChoiceField(
        label='Kategorija', choices=IMAGE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    

class ImageAnnotationForm(forms.ModelForm):
    x_coordinate = forms.FloatField(widget=forms.HiddenInput())
    y_coordinate = forms.FloatField(widget=forms.HiddenInput())
    annotation_text = forms.CharField(label='Anotacijos tekstas', widget=forms.Textarea(attrs={'class': 'form-control'}), required=False)
    annotation_image = forms.ImageField(label='Anotacijos nuotrauka', widget=forms.ClearableFileInput(attrs={'class': 'form-control'}), required=False)
    class Meta:
        model = ImageAnnotation
        fields = ['x_coordinate', 'y_coordinate', 'annotation_text', 'annotation_image']

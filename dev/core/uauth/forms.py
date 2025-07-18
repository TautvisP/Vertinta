from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth import authenticate
from core.uauth.models import User, UserMeta, AgencyInvitation
from django.utils.translation import gettext as _

class LoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}), label="Email")
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'password')

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(self.request, email=email, password=password)

            if self.user_cache is None:

                if not User.objects.filter(email=email).exists():
                    raise forms.ValidationError(_("Paskyra su šiuo El. paštu nerasta."))
                else:
                    raise forms.ValidationError(_("Neteisingas slaptažodis."))
                
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def get_invalid_login_error(self):
        return forms.ValidationError(
            _("Neteisingas El. paštas arba slaptažodis."),
            code='invalid_login',
        )


class EvaluatorRegisterForm(UserCreationForm):
    name = forms.CharField(
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
        fields = ('name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()

        return user


class RegisterForm(UserCreationForm):
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


class AgencyRegisterForm(UserCreationForm):
    agency_name = forms.CharField(
        label=_('Agentūros pavadinimas'), 
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
        fields = ('email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)

        if commit:
            user.save()
            self.save_meta(user)

        return user

    def save_meta(self, user):
        UserMeta.objects.update_or_create(
            user=user, meta_key='agency_name', defaults={'meta_value': self.cleaned_data['agency_name']}
        )


class UserEditForm(UserChangeForm):
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
    phone_num = forms.CharField(
        label=_('Tel. Nr.'), 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone_num'].initial = UserMeta.get_meta(self.instance, 'phone_num')

    def save(self, commit=True):
        user = super().save(commit=False)

        if commit:
            user.save()
            self.save_meta(user)

        return user

    def save_meta(self, user):
        UserMeta.objects.update_or_create(
            user=user, meta_key='phone_num', defaults={'meta_value': self.cleaned_data['phone_num']}
        )


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label=_('Senas slaptažodis'), 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label=_('Naujas slaptažodis'), 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label=_('Pakartokite slaptažodį'), 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )




class AgencyInvitationForm(forms.ModelForm):
    email = forms.EmailField(
        label=_('El. paštas'), 
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = AgencyInvitation
        fields = ('email',)
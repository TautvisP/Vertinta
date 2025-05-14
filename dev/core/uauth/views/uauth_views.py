from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic.edit import CreateView, UpdateView
from django.contrib import messages
from core.uauth.forms import *
from core.uauth.models import *
from django.contrib.auth.models import Group
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext as _
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from shared.mixins.mixins import UserRoleContextMixin
from django.shortcuts import get_object_or_404

# Global message variables
MISTAKE_MESSAGE = _("Pataisykite klaidas.")
FAILED_REGISTRATION_MESSAGE = _("Registracija nepavyko. Ištaisykite klaidas.")
NO_PERMISSION_MESSAGE = _("Neturite leidimo pasiekti šį puslapį.")

class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'uauth/login.html'


    def get_success_url(self):
        user = self.request.user
        if user.groups.filter(name='Agency').exists():
            return reverse_lazy('modules.orders:order_list')
        
        elif user.groups.filter(name='Evaluator').exists():
            return reverse_lazy('modules.orders:evaluator_order_list')
        
        return reverse_lazy('modules.orders:selection')


    def form_valid(self, form):
        return super().form_valid(form)


    def form_invalid(self, form):
        for error in form.errors.values():
            messages.error(self.request, error)

        return super().form_invalid(form)




class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('core.uauth:login')




class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = 'uauth/register.html'
    success_url = reverse_lazy('core.uauth:login')


    def form_valid(self, form):
        messages.success(self.request, _("Registracija sėkminga! Prisijunkite."))
        return super().form_valid(form)


    def form_invalid(self, form):
        messages.error(self.request, FAILED_REGISTRATION_MESSAGE)
        return super().form_invalid(form)
    



class AgencyRegisterWithTokenView(CreateView):
    model = User
    form_class = AgencyRegisterForm
    template_name = 'uauth/agency_register.html'
    success_url = reverse_lazy('core.uauth:login')
    
    def dispatch(self, request, *args, **kwargs):
        # Get and validate the token
        token = self.kwargs.get('token')
        try:
            self.invitation = AgencyInvitation.objects.get(token=token)
            
            if self.invitation.is_used:
                messages.error(request, _("Šis kvietimas jau buvo panaudotas."))
                return redirect('core.uauth:login')
                
            if self.invitation.is_expired:
                messages.error(request, _("Šis kvietimas nebegalioja."))
                return redirect('core.uauth:login')
                
        except AgencyInvitation.DoesNotExist:
            messages.error(request, _("Neteisingas kvietimo kodas."))
            return redirect('core.uauth:login')
            
        return super().dispatch(request, *args, **kwargs)
    
    def get_initial(self):
        # Pre-fill the email field with the invited email
        return {'email': self.invitation.email}
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = True
        user.save()
        
        agency_group, created = Group.objects.get_or_create(name='Agency')
        user.groups.add(agency_group)
        
        self.invitation.is_used = True
        self.invitation.save()
        
        messages.success(self.request, _("Agentūros registracija sėkminga! Prisijunkite."))
        return super().form_valid(form)




class UserEditView(LoginRequiredMixin, UserPassesTestMixin, UserRoleContextMixin, UpdateView):
    model = User
    form_class = UserEditForm
    form_class_password = UserPasswordChangeForm
    template_name = 'uauth/user_edit.html'
    success_url = reverse_lazy('core.uauth:edit_profile')
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

    def test_func(self):
        return not (self.request.user.groups.filter(name='Agency').exists() or self.request.user.groups.filter(name='Evaluator').exists())

    def handle_no_permission(self):
        messages.error(self.request, NO_PERMISSION_MESSAGE)
        return redirect('core.uauth:login')

    def get_object(self):
        return self.request.user


    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        password_form = self.form_class_password(self.request.user, self.request.POST)

        if 'update_profile' in request.POST and form.is_valid():
            return self.form_valid(form)
        
        elif 'change_password' in request.POST and password_form.is_valid():
            return self.password_form_valid(password_form)
        
        else:
            return self.form_invalid(form, password_form)


    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, _("Profilis sėkmingai atnaujintas!"), extra_tags='profile')
        return super().form_valid(form)


    def password_form_valid(self, password_form):
        user = password_form.save()
        update_session_auth_hash(self.request, user)
        messages.success(self.request, _("Slaptažodis sėkmingai pakeistas!"), extra_tags='password')
        return super().form_valid(password_form)


    def form_invalid(self, form, password_form=None):

        if password_form and not password_form.is_valid():
            messages.error(self.request, _("Klaida keičiant slaptažodį."), extra_tags='password')
            return self.render_to_response(self.get_context_data(form=form, password_form=password_form))
        
        messages.error(self.request, _("Klaida atnaujinant profilį."), extra_tags='profile')
        return self.render_to_response(self.get_context_data(form=form))


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        initial_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone_num': UserMeta.get_meta(user, 'phone_num'),
        }
        context['form'] = self.form_class(instance=user, initial=initial_data)
        context['password_form'] = self.form_class_password(self.request.user)
        return context
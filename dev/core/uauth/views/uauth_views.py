from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.contrib import messages
from core.uauth.forms import *
from core.uauth.models import *
from django.contrib.auth.models import Group
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext as _

# Global message variables
MISTAKE_MESSAGE = _("Pataisykite klaidas.")
FAILED_REGISTRATION_MESSAGE = _("Registracija nepavyko. Ištaisykite klaidas.")

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
        messages.success(self.request, _("Pavyko prisijungti!"))
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
    



class AgencyRegisterView(CreateView):
    model = User
    form_class = AgencyRegisterForm
    template_name = 'uauth/agency_register.html'
    success_url = reverse_lazy('core.uauth:login')


    def form_valid(self, form):
        user = form.save()
        agency_group = Group.objects.get(name='Agency')
        user.groups.add(agency_group)
        messages.success(self.request, _("Agentūros registracija sėkminga! Prisijunkite."))
        return super().form_valid(form)


    def form_invalid(self, form):
        messages.error(self.request, FAILED_REGISTRATION_MESSAGE)
        return super().form_invalid(form)
    



class EvaluatorRegisterView(CreateView):
    model = User
    form_class = EvaluatorRegisterForm
    template_name = 'uauth/evaluator_register.html'
    success_url = reverse_lazy('core.uauth:login')


    def form_valid(self, form):
        user = form.save()
        evaluator_group = Group.objects.get(name='Evaluator')
        user.groups.add(evaluator_group)
        messages.success(self.request, _("Vertintojo registracija sėkminga! Prisijunkite."))
        return super().form_valid(form)


    def form_invalid(self, form):
        messages.error(self.request, FAILED_REGISTRATION_MESSAGE)
        return super().form_invalid(form)




class UserEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserEditForm
    form_class_password = UserPasswordChangeForm
    template_name = 'uauth/user_edit.html'
    success_url = reverse_lazy('core.uauth:edit_profile')
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'


    def get_object(self):
        return self.request.user


    def form_valid(self, form):
        user = form.save()
        password_form = self.form_class_password(user, self.request.POST)


        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(self.request, user)
            messages.success(self.request, _("Profilis sėkmingai atnaujintas!"))

        else:
            messages.error(self.request, MISTAKE_MESSAGE)

        return super().form_valid(form)


    def form_invalid(self, form):
        messages.error(self.request, MISTAKE_MESSAGE)
        return super().form_invalid(form)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['password_form'] = self.form_class_password(self.request.user)
        return context
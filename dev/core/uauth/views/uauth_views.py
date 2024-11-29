from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.contrib import messages
from core.uauth.forms import *
from core.uauth.models import *
from django.contrib.auth.models import Group
from django.contrib.auth import update_session_auth_hash, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin

class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'uauth/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.groups.filter(name='Agency').exists():
            return reverse_lazy('modules.orders:order_list')
        
        return reverse_lazy('modules.orders:selection')

    def form_valid(self, form):
        messages.success(self.request, "Login successful!")
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
        messages.success(self.request, "Registration successful! Please log in.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Registration failed. Please correct the errors below.")
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
        messages.success(self.request, "Agency registration successful! Please log in.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Registration failed. Please correct the errors below.")
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
        messages.success(self.request, "Evaluator registration successful! Please log in.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Registration failed. Please correct the errors below.")
        return super().form_invalid(form)


class UserEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserEditForm
    template_name = 'uauth/user_edit.html'
    success_url = reverse_lazy('core.uauth:edit_profile')
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        user = form.save()
        password_form = UserPasswordChangeForm(user, self.request.POST)

        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(self.request, user)
            messages.success(self.request, 'Your profile was successfully updated!')

        else:
            messages.error(self.request, 'Please correct the error below.')

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the error below.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['password_form'] = UserPasswordChangeForm(self.request.user)
        return context
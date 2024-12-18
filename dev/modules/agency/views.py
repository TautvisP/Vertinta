from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from modules.agency.forms import AgencyEditForm, AgencyPasswordChangeForm, EvaluatorCreationForm
from core.uauth.models import User, UserMeta, Group
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import UpdateView, CreateView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.utils.translation import gettext as _

# Global message variables
SUCCESS_MESSAGE = _("Profilis sėkmingai atnaujintas!")
MISTAKE_MESSAGE = _("Pataisykite klaidas.")
NO_PERMISSION_MESSAGE = _("Neturite leidimo pasiekti šį puslapį.")



def index(request):
    return render(request, 'agency/index.html')




class EditAgencyAccountView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    model_meta = UserMeta
    form_class = AgencyEditForm
    form_class_password = AgencyPasswordChangeForm
    template_name = 'edit_agency_account.html'
    success_url = reverse_lazy('modules.agency:edit_agency_account')
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'


    def test_func(self):
        return self.request.user.groups.filter(name='Agency').exists()


    def handle_no_permission(self):
        messages.error(self.request, NO_PERMISSION_MESSAGE)
        return redirect('core.uauth:login')


    def get_object(self, queryset=None):
        return self.request.user


    def get_initial(self):
        initial = super().get_initial()
        user = self.get_object()
        initial.update({
            'agency_name': self.model_meta.get_meta(user, 'agency_name'),
            'main_city': self.model_meta.get_meta(user, 'main_city'),
            'phone_num': self.model_meta.get_meta(user, 'phone_num'),
            'evaluation_starting_price': self.model_meta.get_meta(user, 'evaluation_starting_price'),
        })
        return initial


    def form_valid(self, form):
        user = form.save()
        password_form = self.form_class_password(user, self.request.POST)

        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(self.request, user)
            messages.success(self.request, SUCCESS_MESSAGE)
        else:
            messages.error(self.request, MISTAKE_MESSAGE)

        return super().form_valid(form)


    def form_invalid(self, form):
        messages.error(self.request, MISTAKE_MESSAGE)
        return super().form_invalid(form)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['password_form'] = self.form_class_password(self.request.user)
        context['is_agency'] = self.request.user.groups.filter(name='Agency').exists()

        return context
    



class EvaluatorListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'evaluator_list.html'
    context_object_name = 'evaluators'
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'


    def test_func(self):
        return self.request.user.groups.filter(name='Agency').exists()


    def handle_no_permission(self):
        messages.error(self.request, NO_PERMISSION_MESSAGE)
        return redirect('core.uauth:login')


    def get_queryset(self):
        return self.model.objects.filter(agency=self.request.user)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        evaluators = self.get_queryset()
        evaluator_data = []

        for evaluator in evaluators:
            evaluator_data.append({
                'id': evaluator.id,
                'first_name': evaluator.first_name,
                'last_name': evaluator.last_name,
                'email': evaluator.email,
                'phone_num': UserMeta.get_meta(evaluator, 'phone_num'),
                'date_joined': evaluator.date_joined,
            })

        context['evaluator_data'] = evaluator_data
        context['is_agency'] = self.request.user.groups.filter(name='Agency').exists()
        context['title'] = 'Evaluators in Agency'
        return context




class CreateEvaluatorAccountView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = User
    form_class = EvaluatorCreationForm
    template_name = 'create_evaluator_account.html'
    success_url = reverse_lazy('modules.agency:evaluator_list')
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'


    def test_func(self):
        return self.request.user.groups.filter(name='Agency').exists()


    def handle_no_permission(self):
        messages.error(self.request, NO_PERMISSION_MESSAGE)
        return redirect('core.uauth:login')


    def form_valid(self, form):
        user = form.save(commit=False)
        user.agency = self.request.user
        user.save()
        evaluator_group = Group.objects.get(name='Evaluator')
        user.groups.add(evaluator_group)
        messages.success(self.request, _("Vertintojo paskyra sėkmingai sukurta!"))
        return super().form_valid(form)


    def form_invalid(self, form):
        messages.error(self.request, _("Vertintojo paskyra nebuvo sukurta. Pataisykite klaidas."))
        return super().form_invalid(form)
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_agency'] = self.request.user.groups.filter(name='Agency').exists()
        return context
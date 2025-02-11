from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from shared.mixins.mixins import UserRoleContextMixin
from modules.agency.forms import AgencyEditForm, AgencyPasswordChangeForm, EvaluatorCreationForm
from core.uauth.models import User, UserMeta, Group
from modules.orders.models import Order
from django.urls import reverse_lazy
from django.views.generic import ListView, View
from django.views.generic.edit import UpdateView, CreateView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.utils.translation import gettext as _
from modules.orders.enums import STATUS_CHOICES

# Global message variables
SUCCESS_MESSAGE = _("Profilis sėkmingai atnaujintas!")
MISTAKE_MESSAGE = _("Pataisykite klaidas.")
NO_PERMISSION_MESSAGE = _("Neturite leidimo pasiekti šį puslapį.")


def index(request):
    return render(request, 'agency/index.html')



class EditAgencyAccountView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    View to edit the agency account details. Has seperate forms in the same window for general account info
    and password change.
    Requires the user to be logged in and have the 'Agency' role.
    """
    
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
        messages.success(self.request, SUCCESS_MESSAGE, extra_tags='profile')
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
            'agency_name': self.model_meta.get_meta(user, 'agency_name'),
            'main_city': self.model_meta.get_meta(user, 'main_city'),
            'phone_num': self.model_meta.get_meta(user, 'phone_num'),
            'email': user.email,
            'evaluation_starting_price': self.model_meta.get_meta(user, 'evaluation_starting_price'),
        }
        context['form'] = self.form_class(initial=initial_data)
        context['password_form'] = self.form_class_password(self.request.user)
        context['is_agency'] = self.request.user.groups.filter(name='Agency').exists()
        return context




class EvaluatorListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    View to display a list of evaluators for the current agency. Shows each evaluators data and order counts.
    Requires the user to be logged in and have the 'Agency' role.
    """
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

        new_status = STATUS_CHOICES[1][0]
        ongoing_status = STATUS_CHOICES[3][0]
        completed_status = STATUS_CHOICES[4][0]

        for evaluator in evaluators:
            new_orders_count = Order.objects.filter(evaluator=evaluator, status=new_status).count()
            ongoing_orders_count = Order.objects.filter(evaluator=evaluator, status=ongoing_status).count()
            completed_orders_count = Order.objects.filter(evaluator=evaluator, status=completed_status).count()
            evaluator_data.append({
                'id': evaluator.id,
                'first_name': evaluator.first_name,
                'last_name': evaluator.last_name,
                'email': evaluator.email,
                'phone_num': UserMeta.get_meta(evaluator, 'phone_num'),
                'date_joined': evaluator.date_joined,
                'new_orders_count': new_orders_count,
                'ongoing_orders_count': ongoing_orders_count,
                'completed_orders_count': completed_orders_count,
            })

        context['evaluator_data'] = evaluator_data
        context['is_agency'] = self.request.user.groups.filter(name='Agency').exists()
        context['title'] = 'Evaluators in Agency'
        return context




class CreateEvaluatorAccountView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    View to create a new evaluator account by completing the form.
    Requires the user to be logged in and have the 'Agency' role.
    """
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
    



class ReassignEvaluatorView(LoginRequiredMixin, UserRoleContextMixin, ListView):
    """
    View to reassign an evaluator to an order. Transfers the order to the new evaluator and keeps 
    the progress made by the last evaluator. Used to load the template and display the evaluators' data.
    Requires the user to be logged in and have the appropriate role.
    """
    model = User
    template_name = 'reassign_evaluator.html'
    context_object_name = 'evaluators'
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'


    def get_queryset(self):
        return self.model.objects.filter(groups__name='Evaluator')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_id'] = self.kwargs.get('order_id')
        evaluators = self.get_queryset()
        evaluator_data = []

        ongoing_status = STATUS_CHOICES[3][0]
        completed_status = STATUS_CHOICES[4][0]

        for evaluator in evaluators:
            evaluator_data.append({
                'id': evaluator.id,
                'first_name': evaluator.first_name,
                'last_name': evaluator.last_name,
                'email': evaluator.email,
                'ongoing_orders_count': evaluator.evaluator_orders.filter(status=ongoing_status).count(),
                'completed_orders_count': evaluator.evaluator_orders.filter(status=completed_status).count(),
            })

        context['evaluator_data'] = evaluator_data
        return context




class AssignEvaluatorView(LoginRequiredMixin, UserRoleContextMixin, View):
    """
    View to assign a new evaluator to an order. Used to complete the reasigning process.
    Requires the user to be logged in and have the appropriate role.
    """
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

    def post(self, request, *args, **kwargs):
        order_id = self.kwargs.get('order_id')
        evaluator_id = self.kwargs.get('evaluator_id')
        order = get_object_or_404(Order, id=order_id)
        new_evaluator = get_object_or_404(User, id=evaluator_id)

        # Assign the new evaluator to the order
        order.evaluator = new_evaluator
        order.save()

        messages.success(request, _("Vertintojas sėkmingai priskirtas!"))
        return redirect('modules.orders:specific_evaluator_order_list', id=evaluator_id)
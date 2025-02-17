"""
This view contains the views for the evaluator module.
The views are responsible for handling some of the evaluation process steps and the evaluator's account management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from core.uauth.models import UserMeta
from shared.mixins.mixins import UserRoleContextMixin
from core.uauth.models import User
from modules.orders.models import Object, Order
from django.views.generic import TemplateView
from modules.evaluator.forms import EvaluatorEditForm, EvaluatorPasswordChangeForm
from django.utils.translation import gettext as _
from shared.mixins.evaluator_access_mixin import EvaluatorAccessMixin


# Global message variables
SUCCESS_MESSAGE = _("Profilis sėkmingai atnaujintas!")
MISTAKE_MESSAGE = _("Pataisykite klaidas.")
NO_PERMISSION_MESSAGE = _("Neturite leidimo pasiekti šį puslapį.")

# Global context variables
TOTAL_STEPS = 8
SHOW_PROGRESS_BAR = True

def index(request):
    return render(request, 'evaluator/index.html')




class EditEvaluatorAccountView(LoginRequiredMixin, UserPassesTestMixin, UserRoleContextMixin, UpdateView):
    """
    This view is used for the evaluator to edit their own account. It is also used for the agency to edit the evaluator's account
    """

    model = User
    model_meta = UserMeta
    form_class = EvaluatorEditForm
    form_class_password = EvaluatorPasswordChangeForm
    template_name = 'edit_evaluator_account.html'
    success_url = reverse_lazy('modules.evaluator:edit_own_evaluator_account')
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'


    def get_success_url(self):
        return reverse_lazy('modules.evaluator:edit_own_evaluator_account')


    def test_func(self):
        user = self.request.user
        return user.groups.filter(name__in=['Agency', 'Evaluator']).exists()


    def handle_no_permission(self):
        messages.error(self.request, NO_PERMISSION_MESSAGE)
        return redirect('core.uauth:login')


    def get_object(self, queryset=None):

        if self.request.user.groups.filter(name='Agency').exists() and 'pk' in self.kwargs:
            return self.model.objects.get(pk=self.kwargs['pk'])
        
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
            'qualification_certificate_number': UserMeta.get_meta(user, 'qualification_certificate_number'),
            'date_of_issue_of_certificate': UserMeta.get_meta(user, 'date_of_issue_of_certificate'),
            'phone_num': UserMeta.get_meta(user, 'phone_num'),  # Retrieve phone_num from UserMeta
        }
        context['form'] = self.form_class(instance=user, initial=initial_data)
        context['password_form'] = self.form_class_password(self.request.user)
        return context



class EvaluationStepsView(LoginRequiredMixin, EvaluatorAccessMixin, TemplateView):
    """
    Acts as a hub for the multi-step evaluation process. 
    This view provides the evaluator with the ability to see and navigate through the evaluation steps
    """

    template_name = "evaluation_steps.html"
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        context['order'] = order
        return context





class RCDataEditView(LoginRequiredMixin, EvaluatorAccessMixin, TemplateView):
    """
    Third step of the evaluation process. This view should be responsible for getting and displaying data from "Registru Centras".
    For now it is just a placeholder
    """

    model = Object
    user_meta = UserMeta
    template_name = "edit_RC_data.html"
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

    def get_success_url(self):
        return reverse_lazy('modules.evaluator:edit_gallery', kwargs={'order_id': self.kwargs['order_id'], 'pk': self.kwargs['pk']})


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        obj = order.object
        client = order.client
        phone_number = self.user_meta.get_meta(client, 'phone_num')
        context['order'] = order
        context['object'] = obj
        context['client'] = client
        context['phone_number'] = phone_number
        context['order_id'] = self.kwargs['order_id']
        context['pk'] = self.kwargs['pk']
        context['show_progress_bar'] = SHOW_PROGRESS_BAR
        context['is_evaluator'] = True
        context['current_step'] = 3
        context['total_steps'] = TOTAL_STEPS

        return context
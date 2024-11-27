from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from core.uauth.models import UserMeta
from modules.evaluator.forms import EvaluatorEditForm, EvaluatorPasswordChangeForm
from core.uauth.models import User

def index(request):
    return render(request, 'evaluator/index.html')


@method_decorator(login_required, name='dispatch')
class EditEvaluatorAccountView(UserPassesTestMixin, UpdateView):
    model = User
    form_class = EvaluatorEditForm
    template_name = 'edit_evaluator_account.html'

    def get_success_url(self):
        return reverse_lazy('modules.evaluator:edit_evaluator_account', kwargs={'pk': self.object.pk})

    def test_func(self):
        user = self.request.user
        return user.groups.filter(name__in=['Agency', 'Evaluator']).exists()

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to access this page.")
        return redirect('core.uauth:login')

    def get_object(self, queryset=None):
        if self.request.user.groups.filter(name='Agency').exists() and 'pk' in self.kwargs:
            return User.objects.get(pk=self.kwargs['pk'])
        return self.request.user

    def get_initial(self):
        initial = super().get_initial()
        user = self.get_object()
        initial.update({
            'name': user.first_name,
            'last_name': user.last_name,
            'qualification_certificate_number': UserMeta.get_meta(user, 'qualification_certificate_number'),
            'date_of_issue_of_certificate': UserMeta.get_meta(user, 'date_of_issue_of_certificate'),
            'phone_num': UserMeta.get_meta(user, 'phone_num'),
        })
        return initial

    def form_valid(self, form):
        user = form.save()
        password_form = EvaluatorPasswordChangeForm(user, self.request.POST)
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
        context['password_form'] = EvaluatorPasswordChangeForm(self.request.user)
        return context
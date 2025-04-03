from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import update_session_auth_hash
from modules.orders.utils import create_report_approval_notification, create_order_reassignment_notification, create_event_transfer_notification, create_report_rejection_notification, create_order_assignment_notification
from django.contrib import messages
from shared.mixins.mixins import UserRoleContextMixin
from modules.agency.forms import AgencyEditForm, AgencyPasswordChangeForm, EvaluatorCreationForm
from core.uauth.models import User, UserMeta, Group
from modules.orders.models import Order, Report, Event
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, View, DetailView
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


    def test_func(self):
        return self.request.user.groups.filter(name='Agency').exists()

    def handle_no_permission(self):
        messages.error(self.request, NO_PERMISSION_MESSAGE)
        return redirect('core.uauth:login')
    
    def dispatch(self, request, *args, **kwargs):
        """
        Override the dispatch method to enforce role-based access control.
        """
        if not self.test_func():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


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

    def test_func(self):
        return self.request.user.groups.filter(name='Agency').exists()

    def handle_no_permission(self):
        messages.error(self.request, NO_PERMISSION_MESSAGE)
        return redirect('core.uauth:login')
    
    def dispatch(self, request, *args, **kwargs):
        """
        Override the dispatch method to enforce role-based access control.
        """
        if not self.test_func():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        order_id = self.kwargs.get('order_id')
        evaluator_id = self.kwargs.get('evaluator_id')
        order = get_object_or_404(Order, id=order_id)
        new_evaluator = get_object_or_404(User, id=evaluator_id)
        old_evaluator = order.evaluator

        order.evaluator = new_evaluator
        order.save()

        events_transferred = self.transfer_calendar_events(order, old_evaluator, new_evaluator)

        create_order_assignment_notification(order, new_evaluator, request.user)

        event_count = Event.objects.filter(order=order).count()
        if event_count > 0:
            create_event_transfer_notification(order, new_evaluator, event_count, request.user)

        if old_evaluator:
            create_order_reassignment_notification(
                order, 
                old_evaluator, 
                new_evaluator, 
                request.user, 
                events_transferred
            )
        messages.success(request, _("Vertintojas sėkmingai priskirtas!"))
        return redirect('modules.orders:specific_evaluator_order_list', id=evaluator_id)


    def transfer_calendar_events(self, order, old_evaluator, new_evaluator):
        """
        Transfer calendar events associated with this order to the new evaluator.
        
        Calendar events created by the old evaluator will now show as created by the new evaluator.
        This ensures all calendar events for the order remain associated with the current evaluator.
        """
        # Import Event model here to avoid circular imports
        from modules.orders.models import Event
        
        if not old_evaluator:
            return 0
        
        # Get all events for this order
        events = Event.objects.filter(order=order)
        
        transfer_count = 0
        # For events created by the old evaluator, update to new evaluator
        for event in events:
            if event.created_by == old_evaluator:
                event.created_by = new_evaluator
                event.save(update_fields=['created_by', 'updated_at'])
                transfer_count += 1
                
        return transfer_count




class ReportReviewView(LoginRequiredMixin, UserPassesTestMixin, UserRoleContextMixin, DetailView):
    """
    View for agencies to review reports.
    """
    model = Order
    template_name = 'report_review.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'
    
    def test_func(self):
        # Only agencies can review reports
        return self.request.user.groups.filter(name='Agency').exists()
    
    def handle_no_permission(self):
        messages.error(self.request, NO_PERMISSION_MESSAGE)
        return redirect('core.uauth:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        
        # Check if report exists
        if not hasattr(order, 'report') or not order.report:
            messages.error(self.request, _("Ši ataskaita neegzistuoja."))
            return redirect('modules.orders:order_list')
            
        context['report'] = order.report
        
        # Check if this agency is associated with this order
        if order.agency != self.request.user:
            messages.error(self.request, _("Jūs neturite teisės peržiūrėti šios ataskaitos."))
            return redirect('modules.orders:order_list')
            
        return context




class ApproveReportView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    View for agencies to approve reports.
    """
    def test_func(self):
        return self.request.user.groups.filter(name='Agency').exists()
    
    def handle_no_permission(self):
        messages.error(self.request, NO_PERMISSION_MESSAGE)
        return redirect('core.uauth:login')
    
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        
        # Check if this agency is associated with this order
        if order.agency != request.user:
            messages.error(request, _("Jūs neturite teisės patvirtinti šios ataskaitos."))
            return redirect('modules.orders:order_list')
        
        # Check if report exists
        if not hasattr(order, 'report') or not order.report:
            messages.error(request, _("Ši ataskaita neegzistuoja."))
            return redirect('modules.orders:order_list')
        
        # Approve report
        order.report.status = 'approved'
        order.report.save()
        
        # Notify client
        self.notify_client(order)

        # Create notifications
        create_report_approval_notification(order.report, request.user)
    
        
        messages.success(request, _("Ataskaita sėkmingai patvirtinta ir išsiųsta klientui."))
        return redirect('modules.orders:order_list')
    
    def notify_client(self, order):
        """Send notification to client about approved report."""
        client = order.client
        
        subject = _("Jūsų užsakymo ataskaita patvirtinta")
        message = f"""
Sveiki, {client.get_full_name()},

Jūsų turto vertinimo užsakymo #{order.id} ataskaita buvo patvirtinta ir dabar yra prieinama jums.
Galite peržiūrėti ataskaitą prisijungę prie sistemos ir pasirinkę savo užsakymą.

Ačiū, kad naudojatės mūsų paslaugomis,
Sistema
        """
        
        try:
            # Print to console for development
            print("\n" + "="*80)
            print("CLIENT NOTIFICATION EMAIL")
            print("="*80)
            print(f"To: {client.email}")
            print(f"Subject: {subject}")
            print(f"Message: {message}")
            print("="*80 + "\n")
            
            # In production you would send the actual email
            # email = EmailMessage(
            #     subject=subject,
            #     body=message,
            #     from_email=settings.DEFAULT_FROM_EMAIL,
            #     to=[client.email],
            # )
            # email.send()
        except Exception as e:
            print(f"Failed to send client notification: {e}")




class RejectReportView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    View for agencies to reject reports with a reason.
    """
    def test_func(self):
        return self.request.user.groups.filter(name='Agency').exists()
    
    def handle_no_permission(self):
        messages.error(self.request, NO_PERMISSION_MESSAGE)
        return redirect('core.uauth:login')
    
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        
        # Check if this agency is associated with this order
        if order.agency != request.user:
            messages.error(request, _("Jūs neturite teisės atmesti šios ataskaitos."))
            return redirect('modules.orders:order_list')
        
        # Check if report exists
        if not hasattr(order, 'report') or not order.report:
            messages.error(request, _("Ši ataskaita neegzistuoja."))
            return redirect('modules.orders:order_list')
        
        # Get rejection reason
        rejection_reason = request.POST.get('rejection_reason', '')
        if not rejection_reason:
            messages.error(request, _("Prašome nurodyti atmetimo priežastį."))
            return redirect('modules.agency:review_report', order_id=order_id)
        
        # Reject report
        order.report.status = 'rejected'
        order.report.rejection_reason = rejection_reason
        order.report.save()
        
        # Notify evaluator
        self.notify_evaluator(order, rejection_reason)

        # Create notification
        create_report_rejection_notification(order.report, request.user, rejection_reason)
        
        messages.success(request, _("Ataskaita atmesta. Vertintojui bus pranešta."))
        return redirect('modules.orders:order_list')
    
    def notify_evaluator(self, order, rejection_reason):
        """Send notification to evaluator about rejected report."""
        evaluator = order.evaluator
        
        subject = _("Ataskaita atmesta")
        message = f"""
Sveiki, {evaluator.get_full_name()},

Jūsų sugeneruota ataskaita užsakymui #{order.id} buvo atmesta agentūros.

Atmetimo priežastis:
{rejection_reason}

Prašome ištaisyti nurodytus trūkumus ir sugeneruoti naują ataskaitą.

Ačiū,
Sistema
        """
        
        try:
            # Print to console for development
            print("\n" + "="*80)
            print("EVALUATOR NOTIFICATION EMAIL")
            print("="*80)
            print(f"To: {evaluator.email}")
            print(f"Subject: {subject}")
            print(f"Message: {message}")
            print("="*80 + "\n")
            
            # In production you would send the actual email
            # email = EmailMessage(
            #     subject=subject,
            #     body=message,
            #     from_email=settings.DEFAULT_FROM_EMAIL,
            #     to=[evaluator.email],
            # )
            # email.send()
        except Exception as e:
            print(f"Failed to send evaluator notification: {e}")
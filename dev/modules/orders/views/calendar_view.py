import json
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext as _
from django.contrib import messages
from django.utils import timezone
from modules.orders.models import Order, Event
from modules.orders.forms import EventForm
from shared.mixins.mixins import UserRoleContextMixin
from modules.orders.utils import create_event_notification


class CalendarView(LoginRequiredMixin, UserRoleContextMixin, ListView):
    """View for displaying the calendar of events."""
    model = Event
    template_name = 'calendar.html'
    context_object_name = 'events'
    

    def get_queryset(self):
        user = self.request.user
        
        # Get events based on user role
        if user.groups.filter(name='Evaluator').exists():
            # Evaluators see events for orders assigned to them
            return Event.objects.filter(order__evaluator=user)
        
        elif user.groups.filter(name='Agency').exists():
            # Agencies see events for all their evaluators' orders
            return Event.objects.filter(order__agency=user)
        
        else:
            # Regular users see events for their own orders
            return Event.objects.filter(order__client=user)
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_evaluator'] = self.request.user.groups.filter(name='Evaluator').exists()
        context['is_agency'] = self.request.user.groups.filter(name='Agency').exists()
        calendar_events = []

        for event in context['events']:
            calendar_events.append({
                'id': event.id,
                'title': event.title,
                'start': event.start_time.isoformat(),
                'end': event.end_time.isoformat(),
                'url': reverse('modules.orders:event_detail', args=[event.id]),
                'backgroundColor': self.get_event_color(event),
                'borderColor': self.get_event_color(event),
                'eventType': event.event_type
            })
        
        context['calendar_events_json'] = json.dumps(calendar_events)
        return context
    

    def get_event_color(self, event):
        """Return color based on event type."""
        colors = {
            'meeting': '#4285F4',
            'deadline': '#EA4335',
            'site_visit': '#FBBC05',
            'other': '#34A853',
        }

        return colors.get(event.event_type, '#4285F4')




class EventCreateView(LoginRequiredMixin, UserPassesTestMixin, UserRoleContextMixin, CreateView):
    """View for creating a new event."""
    model = Event
    form_class = EventForm
    template_name = 'calendar_event_form.html'
    

    def test_func(self):
        return self.request.user.groups.filter(name__in=['Evaluator', 'Agency']).exists()
    

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        if not form.initial.get('start_time'):

            now = timezone.now()
            next_hour = now.replace(minute=0, second=0, microsecond=0) + timezone.timedelta(hours=1)
            form.initial['start_time'] = next_hour
            form.initial['end_time'] = next_hour + timezone.timedelta(hours=1)
            
        return form
    

    def form_valid(self, form):
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        form.instance.order = order
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        recipients = [order.client]

        if self.request.user != order.evaluator:
            recipients.append(order.evaluator)
        
        for recipient in recipients:
            create_event_notification(self.object, recipient, self.request.user)
        
        messages.success(self.request, _("Įvykis sėkmingai sukurtas"))

        return response
    

    def get_success_url(self):
        return_to = self.request.GET.get('return_to')
        if return_to == 'evaluator_orders':
            return reverse('modules.orders:evaluator_order_list')
        return reverse('modules.orders:calendar')
    




class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UserRoleContextMixin, UpdateView):
    """View for updating an existing event."""
    model = Event
    form_class = EventForm
    template_name = 'calendar_event_form.html'


    def test_func(self):
        event = self.get_object()
        user = self.request.user
        
        if event.created_by == user:
            return True
        
        if user.groups.filter(name='Evaluator').exists() and event.order.evaluator == user:
            return True
        
        if user.groups.filter(name='Agency').exists() and event.order.agency == user:
            return True
        
        return False
    

    def form_valid(self, form):
        response = super().form_valid(form)
        event = self.object
        order = event.order
        recipients = [order.client]

        if self.request.user != order.evaluator and order.evaluator:
            recipients.append(order.evaluator)
        
        for recipient in recipients:
            create_event_notification(
                event, 
                recipient, 
                self.request.user, 
                is_update=True
            )
        
        messages.success(self.request, _("Įvykis sėkmingai atnaujintas"))

        return response
    

    def get_success_url(self):
        return reverse('modules.orders:calendar')




class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, UserRoleContextMixin, DeleteView):
    """View for deleting an existing event."""
    model = Event
    template_name = 'calendar_confirm_delete.html'
    success_url = reverse_lazy('modules.orders:calendar')
    

    def test_func(self):
        event = self.get_object()
        user = self.request.user
        
        if event.created_by == user:
            return True
        
        if user.groups.filter(name='Evaluator').exists() and event.order.evaluator == user:
            return True
        
        if user.groups.filter(name='Agency').exists() and event.order.agency == user:
            return True
        
        return False
    

    def delete(self, request, *args, **kwargs):
        event = self.get_object()
        order = event.order
        recipients = [order.client]

        if self.request.user != order.evaluator and order.evaluator:
            recipients.append(order.evaluator)
        
        for recipient in recipients:
            create_event_notification(
                event, 
                recipient, 
                self.request.user, 
                is_deleted=True
            )
        
        messages.success(self.request, _("Įvykis sėkmingai ištrintas"))

        return super().delete(request, *args, **kwargs)




class EventDetailView(LoginRequiredMixin, UserPassesTestMixin, UserRoleContextMixin, DetailView):
    """View for showing event details."""
    model = Event
    template_name = 'calendar_event_detail.html'
    context_object_name = 'event'
    
    def test_func(self):
        event = self.get_object()
        user = self.request.user
        
        if user == event.order.client or user == event.order.evaluator or user == event.order.agency:
            return True
        
        return False




class ConfirmEventView(LoginRequiredMixin, UserPassesTestMixin, UserRoleContextMixin, UpdateView):
    """View for confirming an event."""
    model = Event
    fields = []
    http_method_names = ['post']
    
    def test_func(self):
        event = self.get_object()

        return self.request.user == event.order.client
    

    def form_valid(self, form):
        event = self.get_object()
        event.is_confirmed = True
        event.save()
        create_event_notification(
            event, 
            event.created_by, 
            self.request.user, 
            is_confirmed=True
        )
        
        messages.success(self.request, _("Įvykis sėkmingai patvirtintas"))
        return super().form_valid(form)
    
    
    def get_success_url(self):
        return reverse('modules.orders'
        ':event_detail', args=[self.object.id])
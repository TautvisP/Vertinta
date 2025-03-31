import functools
from django.urls import reverse
from .models import Notification

#Memoization is an optimization technique that stores the results of expensive function calls 
#and returns the cached result when the same inputs occur again.
def memoize(method):
    @functools.wraps(method)
    def memoizer(*args, **kwargs):
        method._cache = getattr(method, '_cache', {})
        key = args
        if key not in method._cache:
            method._cache[key] = method(*args, **kwargs)
        return method._cache[key]
    return memoizer



def create_report_submission_notification(report, sender):
    """Create notification for agency when evaluator submits a report."""
    if not report.order.agency:
        return
        
    agency = report.order.agency
    order = report.order
    
    Notification.objects.create(
        recipient=agency,
        sender=sender,
        notification_type='report_submission',
        title='Naujai ataskaitai reikalinga peržiūra',
        message=f'Nauja ataskaita užsakymui # {order.id} reikalauja jūsų peržiūros.',
        related_order=order,
        related_report=report,
        action_url=reverse('modules.agency:review_report', args=[order.id])
    )

def create_report_approval_notification(report, sender):
    """Create notification for evaluator and client when agency approves a report."""
    evaluator = report.order.evaluator
    client = report.order.client
    order = report.order
    
    # Notify evaluator
    if evaluator:
        Notification.objects.create(
            recipient=evaluator,
            sender=sender,
            notification_type='report_approval',
            title='Ataskaita patvirtinta',
            message=f'Ataskaita užsakymui # {order.id} patvirtinta.',
            related_order=order,
            related_report=report,
            action_url=reverse('modules.evaluator:evaluation_steps', args=[order.id])
        )
    
    # Notify client
    if client:
        Notification.objects.create(
            recipient=client,
            sender=sender,
            notification_type='report_approval',
            title='Ataskaita prieinama',
            message=f'Ataskaita užsakymui # {order.id} patvirtinta.',
            related_order=order,
            related_report=report,
            action_url=reverse('modules.orders:view_report', args=[order.id])
        )

def create_report_rejection_notification(report, sender, reason):
    """Create notification for evaluator when agency rejects a report."""
    evaluator = report.order.evaluator
    order = report.order
    
    if not evaluator:
        return

    Notification.objects.create(
        recipient=evaluator,
        sender=sender,
        notification_type='report_rejection',
        title='Ataskaita atmesta',
        message=f'Jūsų ataskaita užsakymui # {order.id} atmesta. Priežastis: {reason}',
        related_order=order,
        related_report=report,
        action_url=reverse('modules.evaluator:evaluation_steps', args=[order.id])
    )

def create_order_assignment_notification(order, evaluator, sender):
    """Create notification for evaluator when assigned to an order."""
    Notification.objects.create(
        recipient=evaluator,
        sender=sender,
        notification_type='order_assignment',
        title='Naujas užsakymas',
        message=f'Jums priskirtas užsakymas #{order.id}.',
        related_order=order,
        action_url=reverse('modules.evaluator:evaluation_steps', args=[order.id])
    )


def create_event_notification(event, recipient, sender, is_update=False, is_deleted=False, is_confirmed=False):
    """Create notification for event creation, updates, or deletion."""
    order = event.order
    
    if is_deleted:
        title = 'Event Cancelled'
        message = f'Event "{event.title}" for order #{order.id} has been cancelled.'
    elif is_update:
        title = 'Event Updated'
        message = f'Event "{event.title}" for order #{order.id} has been updated.'
    elif is_confirmed:
        title = 'Event Confirmed'
        message = f'Event "{event.title}" for order #{order.id} has been confirmed by the client.'
    else:
        title = 'New Event'
        message = f'New event "{event.title}" has been scheduled for order #{order.id}.'
    
    action_url = reverse('modules.orders:event_detail', args=[event.id])
    if is_deleted:
        action_url = reverse('modules.orders:calendar')
    
    Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type='event',
        title=title,
        message=message,
        related_order=order,
        action_url=action_url
    )